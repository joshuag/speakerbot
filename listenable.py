class NotEventException(Exception):
    pass

def event(func):

    func.is_event = True
    return func

def listenable(klass):
    """
        Class decorator to implement a lightweight event-dispatch model.
        @listenable on the class
        @event on the method you want to monitor


        listeners must implement the function signature of the event exactly (or take *args, **kwargs generically),
        plus a special argument called "event_result" that contains the return value of the method invocation.

        TODO: Make it work with other decorators, inheritance
    """

    def wrapper(method):

        def wrapped(*args, **kwargs):

            self = args[0]

            result = method(*args, **kwargs)

            kwargs["event_result"] = result

            self.dispatch_events(method.__name__, *args, **kwargs)

            return result

        wrapped.is_event = True
        return wrapped

    def attach_listener(self, event, listener):

        if not hasattr(getattr(self, event), "is_event"):

            raise NotEventException("This method hasn't been decorated as an event listener")

        listeners = self._listeners.get(event, [])
        listeners.append(listener)
        self._listeners[event] = listeners

    def dispatch_events(self, method_name, *args, **kwargs):

        for listener in self._listeners.get(method_name, []):
            try:
                #pop off the instance information. We just want the function signature
                listener(*args[1:], **kwargs)
            except Exception as e:
                print "Event listener %s failed. It reported the following: %s" % (listener.__name__, str(e))
    
    for name, method in klass.__dict__.iteritems():

        if hasattr(method, "is_event"):

            setattr(klass, name, wrapper(method))
        
    setattr(klass, "_listeners", {})
    setattr(klass, "attach_listener", attach_listener)
    setattr(klass, "dispatch_events", dispatch_events)

    return klass