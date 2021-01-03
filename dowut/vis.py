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


def main():
    df = load_df()
    grouper = pd.Grouper(key="time", freq="60min")
    props = df[df.event_type == "PropertyNotify"].copy()
    props["delta"] = props.time.diff().apply(lambda d: d.total_seconds() / 60)
    sums = props.groupby([grouper, "wm_class"]).delta.sum().unstack()

    f = sums.fillna(0.0)
    f.index = [i.strftime("%a %H:%M") for i in f.index]
    f = f.apply(lambda x: x/x.sum(), axis=1)

    fig, ax = plt.subplots(1)
    ax = f.plot(kind="bar", stacked=True, ax=ax)
    ax.tick_params(axis="x", which="both", labelrotation=45)
    fig.set_tight_layout(True)
    plt.show()
