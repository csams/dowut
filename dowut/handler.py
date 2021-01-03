import time
from functools import wraps


class EventHandlerRepo(type):
    handlers = []

    def __init__(cls, name, bases, attrs):
        if name != "EventHandler":
            EventHandlerRepo.handlers.append(cls)


class EventHandler(metaclass=EventHandlerRepo):
    MASK = 0

    def __init__(self, disp, root, config_dir):
        self.disp = disp
        self.root = root
        self.config_dir = config_dir

    def idle(self):
        pass

    def close(self):
        pass


def throttle(seconds):
    state = {"last": time.monotonic()}

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            now = time.monotonic()
            last = state["last"]
            if now - last >= seconds:
                state["last"] = now
                return func(*args, **kwargs)
        return inner
    return wrapper
