class NotEventException(Exception):
    pass

def event(func):

    func.is_event = True
    return func

def listenable(klass):

    def wrapper(method):

        def wrapped(*args, **kwargs):

            self = args[0]

            results = method(*args, **kwargs)

            try:
                self.dispatch_events(method.__name__, *args, **kwargs)
            except:
                print "One of your listeners failed. I'm not going to let it ruin my day though."

            return results

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
            #pop off the instance information. We just want the function signature
            listener(*args[1:], **kwargs)
    
    for name, method in klass.__dict__.iteritems():

        if hasattr(method, "is_event"):

            setattr(klass, name, wrapper(method))
        
    setattr(klass, "_listeners", {})
    setattr(klass, "attach_listener", attach_listener)
    setattr(klass, "dispatch_events", dispatch_events)

    return klass