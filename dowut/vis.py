import os
from glob import glob

import matplotlib.pyplot as plt
import pandas as pd


def load_df():
    home = os.environ.get("HOME")
    path = os.path.join(home, ".config", "dowut", "data", "data_*.csv")
    paths = sorted(glob(path))
    return pd.concat(pd.read_csv(path, parse_dates=["time"]) for path in paths)


def main():
    df = load_df()
    grouper = pd.Grouper(key="time", freq="15min")
    f = df.groupby(grouper)["wm_class"].value_counts()
    g = (f / f.groupby("time").sum())  # normalize
    g.unstack().plot.bar(stacked=True)
    plt.show()
