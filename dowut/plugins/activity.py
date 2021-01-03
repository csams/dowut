import os
from datetime import datetime
from Xlib import X

from dowut.handler import EventHandler, throttle
from dowut.csv_writer import CsvWriter


class ActivityRecorder(EventHandler):
    MASK = X.PropertyChangeMask | X.KeyPressMask

    def __init__(self, disp, root, config_dir):
        super().__init__(disp, root, config_dir)
        # property on the root window that always holds the name of the active
        # top level window. Requires Extended Window Manager Hints (EWMH).
        NET_ACTIVE_WINDOW = disp.intern_atom("_NET_ACTIVE_WINDOW")

        # property that holds the name of the window
        self._NET_WM_NAME = disp.intern_atom("_NET_WM_NAME")
        self._WM_NAME = disp.intern_atom("_WM_NAME")

        self._atoms = (NET_ACTIVE_WINDOW, self._NET_WM_NAME, self._WM_NAME)

        data_dir = os.path.join(config_dir, "data")
        fieldnames = [
            "wm_instance",
            "wm_class",
            "window_title",
            "event_type",
            "time"
        ]
        self._writer = CsvWriter(data_dir, fieldnames)
        self._last_window = (None, None)

    def on_PropertyNotify(self, event, focused_window):
        """ Record any window focus or title change. """
        win_id = focused_window.id
        win_title = self._get_window_title(focused_window)
        this_window = (win_id, win_title)

        if event.atom in self._atoms and this_window != self._last_window:
            self._last_window = this_window
            row = self._make_row(event, focused_window)
            self._writer.write(row)

    @throttle(seconds=1.0)
    def on_KeyPress(self, event, focused_window):
        """ Record at most one keypress per second for any window. """
        row = self._make_row(event, focused_window)
        self._writer.write(row)

    def idle(self):
        """
        idle is called every second if at least one second has elapsed since
        the last event.
        """
        self._writer.flush_or_rotate()

    def close(self):
        self._writer.close()

    def _get_window_title(self, window):
        name = window.get_full_text_property(self._NET_WM_NAME)
        name = name or window.get_full_text_property(self._WM_NAME)
        if isinstance(name, bytes):
            name = name.decode("utf-8", "replace")
        return name

    def _make_row(self, event, window):
        wm_instance, wm_class = window.get_wm_class()
        return {
            "wm_instance": wm_instance,
            "wm_class": wm_class,
            "window_title": self._get_window_title(window),
            "event_type": event.__class__.__name__,
            "time": datetime.now().isoformat(),
        }
