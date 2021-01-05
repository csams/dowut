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
    description = """Measure how you spend time by tracking key presses and
    changes to window focus or title."""
    p = argparse.ArgumentParser(description=description)

    p.add_argument("-b", "--between", help="Times in 'HH:MM HH:MM' format.")
    p.add_argument("-c", "--categories", help="Category dictionary (JSON).")
    p.add_argument("-d", "--data", nargs="*", help="Data files to load.")
    p.add_argument("-e", "--end", help="Date in YYYY-MM-DD format.")
    p.add_argument("-s", "--start", help="Date in YYYY-MM-DD format.")

    idle_help = "Max minutes between events before you're considered idle."
    p.add_argument("-i", "--idle", help=idle_help, default=10, type=int)

    freq_help = "Grouping frequency. See pandas freq docs for format."
    p.add_argument("-f", "--freq", help=freq_help, default="60min")
    return p.parse_args()


def load_df(paths=None, freq="60min"):
    if not paths:
        home = os.environ.get("HOME")
        path = os.path.join(home, ".config", "dowut", "data", "data_*.csv")
        paths = sorted(glob(path))
    df = pd.concat(pd.read_csv(path, parse_dates=["time"]) for path in paths)

    df.sort_values("time", inplace=True)
    df.set_index("time", drop=False, inplace=True)

    # If a duration straddles a grouping boundary (say we group hourly and the
    # event lasted from from 5:59 to 6:01), we need one minute allocated to the
    # 5:00 hour and one minute to the 6:00 hour. To make the calculations more
    # straightforward, we insert fake events at the grouping boundaries.
    l = df.time.min().floor(freq)
    u = df.time.max().ceil(freq)
    r = pd.date_range(l, u, freq=freq, closed="left")
    s = pd.Series(r)
    idx = pd.concat([s, df.time]).sort_values()
    df = df.reindex(idx)
    df["time"] = df.index

    # Insert a fake event type at "boundary" times. It inherits all values
    # except event_type from the previous row. This ensures the last event from
    # the previous group crosses the boundary while still having its duration
    # correctly allocated to both groups.
    df["event_type"].fillna("Fake", inplace=True)
    df.fillna(method="ffill", inplace=True)
    df.fillna("Fake", inplace=True)
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


def plot_active(df, ax, freq, title, normalize=False, max_idle=None):
    df = df.copy()

    delta = df.shift(-1).time - df.time
    df["delta"] = delta.apply(lambda d: d.total_seconds() / 60)
    if max_idle:
        df["delta"] = df["delta"].apply(lambda d: d if d <= max_idle else 0)

    grouper = pd.Grouper(key="time", freq=freq)
    sums = df.groupby([grouper, "category"]).delta.sum().unstack()
    f = sums.fillna(0.0)
    label = "minutes"
    if normalize:
        f = f.apply(lambda x: 100 * x / x.sum(), axis=1)  # normalize
        label = "percentage"

    # I never got matplotlib formatters and locators to work.
    # Just do it myself.
    f.index = [i.strftime("%a %H:%M") for i in f.index]

    f.plot(kind="bar", stacked=True, ax=ax, title=title)
    ax.tick_params(axis="x", which="both", labelrotation=45)
    ax.grid(axis="y")
    ax.set_ylabel(label)
    ax.legend(loc="upper left")


def plot_active_totals(df, ax, max_idle=None):
    df = df.copy()
    delta = df.shift(-1).time - df.time
    df["delta"] = delta.apply(lambda d: d.total_seconds() / 60)
    active = df[df.delta <= max_idle] if max_idle else df

    sums = active.groupby("category").delta.sum()
    f = sums.fillna(0.0)

    f.plot(kind="bar", ax=ax, title="Total Active Minutes")
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
    freq = args.freq

    df = load_df(args.data, freq=freq)

    if args.start:
        df = df[df.time >= args.start]

    if args.end:
        df = df[df.time <= args.end]

    if args.between:
        s, e = args.between.split()
        df = df.between_time(s, e)

    cat_dict = load_categories(args.categories)
    df = categorize(df, cat_dict)

    fig, axes = plt.subplots(2)

    max_idle = args.idle
    plot_active(df, axes[0], freq, "Active Minutes", max_idle=max_idle)

    focus_changes = df[df.event_type.str.match("PropertyNotify|Fake")]
    plot_active(focus_changes, axes[1], freq, "Focus", normalize=True)

    fig.set_tight_layout(True)

    plt.show()
