import select
from collections import defaultdict
from contextlib import contextmanager
from Xlib.display import Display
from Xlib import X


_keep_going = True


def make_dispatcher(display, handlers):
    # masks for the events we care about
    masks = X.SubstructureNotifyMask
    for h in handlers:
        masks |= h.MASK

    # the root window - ancestor of all other windows
    root = display.screen().root
    NET_ACTIVE = display.intern_atom("_NET_ACTIVE_WINDOW")

    # helper to tell all windows that we care about their events
    def update_masks():
        for w in root.query_tree().children:
            w.change_attributes(event_mask=masks)

        # Some of Xlib is async. Make sure the windows get the change requests
        display.flush()

    def on_create_notify(event):
        update_masks()

    def get_active_window():
        try:
            active = root.get_full_property(NET_ACTIVE, X.AnyPropertyType)
            win_id = active.value[0]
            return display.create_resource_object('window', win_id)
        except:
            pass

    handler_cache = defaultdict(list)

    def fire_handlers(event):
        window = get_active_window()  # display.get_input_focus().focus
        if not window:
            return

        event_name = event.__class__.__name__

        if event_name not in handler_cache:
            method_name = "on_" + event_name
            for h in handlers:
                method = getattr(h, method_name, None)
                if method is not None:
                    handler_cache[event_name].append(method)

        for handler in handler_cache[event_name]:
            try:
                handler(event, window)
            except Exception as ex:
                print(ex)

    def idle():
        for h in handlers:
            try:
                h.idle()
            except Exception as ex:
                print(ex)

    def dispatch(event):
        if event is not None:
            event_type = event.type
            if event_type == X.CreateNotify:
                on_create_notify(event)
            else:
                fire_handlers(event)
        else:
            idle()

    # tell the root window we care about certain events on it.
    root.change_attributes(event_mask=masks)

    # tell the rest of the windows we care about certain events.
    update_masks()

    return dispatch


@contextmanager
def Xdisplay():
    disp = None
    try:
        disp = Display()
        yield disp
    except:
        if disp is not None:
            disp.close()
        raise


def watch(display, handlers):
    dispatch = make_dispatcher(display, handlers)
    while _keep_going:
        readable, w, x = select.select([display], [], [], 1)
        if readable:
            i = display.pending_events()
            while i > 0:
                dispatch(display.next_event())
                i -= 1
        else:
            dispatch(None)


def terminate(*args, **kwargs):
    global _keep_going
    _keep_going = False
