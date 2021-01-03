import importlib
import pkgutil


def load(path, continue_on_error=False):
    try:
        mod = importlib.import_module(path)
    except:
        if continue_on_error:
            return
        raise

    if not hasattr(mod, "__path__"):
        return

    path = mod.__path__
    prefix = mod.__name__ + "."
    for loader, name, ispkg in pkgutil.iter_modules(path=path, prefix=prefix):
        if not name.startswith(prefix):
            name = prefix + name
        load(name)
