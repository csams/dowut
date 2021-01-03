import argparse
import json
import os
import re
from glob import glob

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("dark")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--data", nargs="*", help="Data files to load.")
    p.add_argument("-c", "--categories", help="Category dictionary (JSON).")
    p.add_argument("-f", "--freq", help="Grouping frequency.", default="60min")
    return p.parse_args()


def load_df(paths=None):
    if not paths:
        home = os.environ.get("HOME")
        path = os.path.join(home, ".config", "dowut", "data", "data_*.csv")
        paths = sorted(glob(path))
    df = pd.concat(pd.read_csv(path, parse_dates=["time"]) for path in paths)

    df.sort_values("time", inplace=True)
    return df


def load_config(path):
    with open(path) as f:
        return json.load(f)


def plot_focus_changes(df, ax, freq):
    df = df.copy()
    df["delta"] = df.time.diff().apply(lambda d: d.total_seconds() / 60)
    active = df[df.delta <= 10]

    grouper = pd.Grouper(key="time", freq=freq)
    sums = active.groupby([grouper, "category"]).delta.sum().unstack()
    f = sums.fillna(0.0)
    f = f.apply(lambda x: 100 * x / x.sum(), axis=1)  # normalize

    f.index = [i.strftime("%a %H:%M") for i in f.index]

    f.plot(kind="bar", stacked=True, ax=ax, title="Activity")
    ax.tick_params(axis="x", which="both", labelrotation=45)
    ax.grid(axis="y")
    ax.set_ylabel("percentage")
    ax.legend(loc="upper left")


def plot_active(df, ax, freq):
    df = df.copy()
    df["delta"] = df.time.diff().apply(lambda d: d.total_seconds() / 60)
    active = df[df.delta <= 10]

    grouper = pd.Grouper(key="time", freq=freq)
    sums = active.groupby([grouper, "category"]).delta.sum().unstack()
    f = sums.fillna(0.0)

    f.index = [i.strftime("%a %H:%M") for i in f.index]

    f.plot(kind="bar", ax=ax, stacked=True)
    ax.tick_params(axis="x", which="both", labelrotation=45)
    ax.grid(axis="y")
    ax.set_ylabel("minutes")
    ax.legend(loc="upper left")


def plot_category_totals(df, ax):
    df = df.copy()
    df["delta"] = df.time.diff().apply(lambda d: d.total_seconds() / 60)
    active = df[df.delta <= 10]

    sums = active.groupby("category").delta.sum()
    f = sums.fillna(0.0)

    f.plot(kind="bar", ax=ax)
    ax.tick_params(axis="x", which="both", labelrotation=45)
    ax.grid(axis="y")
    ax.set_ylabel("total minutes")


def categorize(df, conf):
    matchers = {k: [re.compile(m).match for m in ms] for k, ms in conf.items()}

    def inner(row):
        fields = (row.wm_instance, row.wm_class, row.window_title)
        for category, ms in matchers.items():
            if any(m(f) for m in ms for f in fields):
                return category
        else:
            return row.wm_class

    df["category"] = df.apply(inner, axis=1)
    return df


def main():
    args = parse_args()
    df = load_df(args.data)

    cat_dict = load_config(args.categories) if args.categories else {}
    freq = args.freq
    df = categorize(df, cat_dict)

    fig, axes = plt.subplots(3)

    plot_focus_changes(df, axes[0], freq)
    plot_active(df, axes[1], freq)
    plot_category_totals(df, axes[2])

    fig.set_tight_layout(True)

    plt.show()
