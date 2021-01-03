import argparse
import os
import signal
import sys
from daemon import DaemonContext
from dowut.loader import load
from dowut.handler import EventHandlerRepo
from dowut.dispatch import terminate, watch, Xdisplay


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--daemonize", action="store_true", default=False)
    return p.parse_args()


def main():
    handlers = None
    config_dir = os.path.join(os.environ.get("HOME"), ".config", "dowut")
    os.makedirs(config_dir, exist_ok=True)

    plugin_dir = os.path.join(config_dir, "plugins")
    sys.path.insert(0, plugin_dir)

    load("dowut.plugins")
    load(os.environ.get("USER"), continue_on_error=True)

    try:
        with Xdisplay() as disp:
            root = disp.screen().root
            hs = [H(disp, root, config_dir) for H in EventHandlerRepo.handlers]
            watch(disp, hs)
    except Exception as ex:
        print(ex)
        print("\nStopping...")
        if handlers is not None:
            for h in handlers:
                try:
                    h.close()
                except Exception as ex:
                    print(ex)


args = parse_args()
if args.daemonize:
    context = DaemonContext()
    signal_map = {signal.SIGTERM: terminate}
    context.signal_map = signal_map
    with context:
        main()
else:
    main()
