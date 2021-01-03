import os
from csv import DictWriter
from datetime import datetime


class CsvWriter:
    def __init__(self, path, fieldnames):
        self._path = path
        self._fieldnames = fieldnames

        os.makedirs(self._path, exist_ok=True)
        self._file_path = None
        self._file = None
        self._writer = None
        self._last_create = None
        self._create_file()

    def write(self, row):
        try:
            self._writer.writerow(row)
        except:
            self._create_file()
            self._writer.writerow(row)

    def close(self):
        if self._file:
            self._file.close()

    def flush_or_rotate(self):
        if self._last_create is not None:
            now = datetime.now()
            if now.day != self._last_create.day:
                self._create_file()
            else:
                self._file.flush()

    def _create_file(self):
        self.close()

        self._last_create = datetime.now()
        uniq = self._last_create.strftime("%Y%m%d")  # %Y%m%d_%H%M%S
        self._file_path = os.path.join(self._path, f"data_{uniq}.csv")
        self._file = open(self._file_path, mode="a")
        self._writer = DictWriter(self._file, fieldnames=self._fieldnames)
        if self._file.tell() == 0:
            self._writer.writeheader()
