import os
from glob import glob

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("dark")


def load_df():
    home = os.environ.get("HOME")
    path = os.path.join(home, ".config", "dowut", "data", "data_*.csv")
    paths = sorted(glob(path))
    return pd.concat(pd.read_csv(path, parse_dates=["time"]) for path in paths)


def plot_focus_changes(df, ax):
    df = df.copy()
    df["delta"] = df.time.diff().apply(lambda d: d.total_seconds() / 60)
    active = df[df.delta <= 10]

    grouper = pd.Grouper(key="time", freq="60min")
    sums = active.groupby([grouper, "wm_class"]).delta.sum().unstack()

    f = sums.fillna(0.0)
    f.index = [i.strftime("%a %H:%M") for i in f.index]
    f = f.apply(lambda x: 100 * x / x.sum(), axis=1)  # normalize

    f.plot(kind="bar", stacked=True, ax=ax, title="Focused Window")
    ax.tick_params(axis="x", which="both", labelrotation=45)
    ax.grid(axis="y")
    ax.set_ylabel("percentage")


def plot_active(df, ax):
    df = df.copy()
    df["delta"] = df.time.diff().apply(lambda d: d.total_seconds() / 60)
    active = df[df.delta <= 10]

    grouper = pd.Grouper(key="time", freq="60min")
    sums = active.groupby([grouper, "wm_class"]).delta.sum().unstack()

    f = sums.fillna(0.0)
    f.index = [i.strftime("%a %H:%M") for i in f.index]

    f.plot(kind="bar", ax=ax, stacked=True, title="Activity")
    ax.tick_params(axis="x", which="both", labelrotation=45)
    ax.grid(axis="y")
    ax.set_ylabel("minutes")


def main():
    df = load_df()

    fig, axes = plt.subplots(2)

    plot_focus_changes(df, axes[0])
    plot_active(df, axes[1])

    fig.set_tight_layout(True)

    plt.show()
