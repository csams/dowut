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
    p.add_argument("-s", "--start", help="Start in YYYY-MM-DD format.")
    p.add_argument("-e", "--end", help="End in YYYY-MM-DD format.")
    p.add_argument("-b", "--between", help="Times in 'HH:MM HH:MM' format.")

    freq_help = "Grouping frequency. See pandas freq docs for format."
    p.add_argument("-f", "--freq", help=freq_help, default="60min")
    return p.parse_args()


def load_df(paths=None):
    if not paths:
        home = os.environ.get("HOME")
        path = os.path.join(home, ".config", "dowut", "data", "data_*.csv")
        paths = sorted(glob(path))
    df = pd.concat(pd.read_csv(path, parse_dates=["time"]) for path in paths)

    df.sort_values("time", inplace=True)
    df.set_index("time", drop=False, inplace=True)
    return df


def load_categories(path):
    if not path:
        home = os.environ.get("HOME")
        path = os.path.join(home, ".config", "dowut", "categories.json")
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}


def plot_active(df, ax, freq, normalize=False):
    df = df.copy()
    df["delta"] = df.time.diff().apply(lambda d: d.total_seconds() / 60)
    active = df[df.delta <= 10]

    grouper = pd.Grouper(key="time", freq=freq)
    sums = active.groupby([grouper, "category"]).delta.sum().unstack()
    f = sums.fillna(0.0)
    label = "minutes"
    if normalize:
        f = f.apply(lambda x: 100 * x / x.sum(), axis=1)  # normalize
        label = "percentage"

    f.index = [i.strftime("%a %H:%M") for i in f.index]

    f.plot(kind="bar", stacked=True, ax=ax, title="Activity")
    ax.tick_params(axis="x", which="both", labelrotation=45)
    ax.grid(axis="y")
    ax.set_ylabel(label)
    ax.legend(loc="upper left")


def plot_active_totals(df, ax):
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

    if args.start:
        df = df[df.time >= args.start]

    if args.end:
        df = df[df.time <= args.end]

    if args.between:
        s, e = args.between.split()
        df = df.between_time(s, e)

    cat_dict = load_categories(args.categories)
    freq = args.freq
    df = categorize(df, cat_dict)
    df = df[~df.category.str.match("(?i).*dialog")]

    fig, axes = plt.subplots(3)

    plot_active(df, axes[0], freq, normalize=True)
    plot_active(df, axes[1], freq)
    plot_active_totals(df, axes[2])

    fig.set_tight_layout(True)

    plt.show()
