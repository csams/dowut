How do I spend my time?
=======================

`dowut` monitors X events to help you understand how you use your time.
Specifically, it looks for desktop changes, active window changes, window name
changes, and key presses. Consecutive property changes for the same window are
deduplicated, and key press logs are throttled to one per second (the value of
the keys are not recorded).

"Activity" counts as any stretch of time where less than 10 minutes elapses
between two consecutive events.

Install by cloning the project and pip installing it (python 3.6+ required).

Start the daemon in the foreground with `dowutd` or in the background with
`dowutd -d`. To stop the background process, find the PID and `kill -15 <pid>`.

The `dowut` command will display a breakdown of activity by hour and category.

To customize how events are categorized, create a json file where keys are
categories and values are lists of regular expressions. Each regex is tried
against `_WM_NAME`, `_NET_WM_NAME`, (basically the title of the active window)
and both elements of `WM_CLASS`. The first category with a regex that matches
is used. Otherwise, the second element of `WM_CLASS` is used.

Use `xprop` to see the properies of any X window.

`dowut -c <file>` will use the custom category mapping.

```json
{
    "chat": [
        ".*chat.google.com.*",
        ".*Discord.*",
        ".*Slack.*"
    ],
    "email": [
        ".*Red Hat Mail.*"
    ],
    "youtube": [
        ".*YouTube.*"
    ],
    "video meeting": [
        "Meet.*",
        "Blue Jeans.*"
    ]
}
```

All data files are loaded by default. To specify a subset, use the `-d` option
to give one or more direct paths to the individual data files stored in
`$HOME/.config/dowut/data`).

The default grouping frequency is 60 minutes. To change it use the `-f` option
and provide a valid freq as described [in the pandas documentation](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).
