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

            if self.dispatch_events(self._interrogators, method.__name__, *args, **kwargs):

                args, kwargs = self.run_manglers(method.__name__, *args, **kwargs)

                result = method(*args, **kwargs)

                kwargs["event_result"] = result

                self.dispatch_events(self._listeners, method.__name__, *args, **kwargs)

                return result

        wrapped.is_event = True
        return wrapped


    def _attach(self, event, func, handler_collection_name):
        
        #TEMPORARILY REMOVED WHILE I FIGURE OUT HOW TO MAKE MULTIPLE DECORATORS HAPPY
        #if not hasattr(getattr(self, event), "is_event"):

        #    raise NotEventException("This method hasn't been decorated as an event listener")

        handler_collection = getattr(self, handler_collection_name)

        handlers = handler_collection.get(event, [])
        handlers.append(func)
        handler_collection[event] = handlers

        setattr(self, handler_collection_name, handler_collection)


    def attach_interrogator(self, event, interrogator):

        _attach(self, event, interrogator, "_interrogators")


    def attach_listener(self, event, listener):

        _attach(self, event, listener, "_listeners")


    def attach_mangler(self, event, listener):

        _attach(self, event, listener, "_manglers")


    def run_manglers(self, method_name, *args, **kwargs):

        for mangler in self._manglers.get(method_name, []):
            try:
                #pop off the instance information. We just want the function signature
                args, kwargs = mangler(*args[1:], **kwargs)
                
            except Exception as e:
                print "Argument mangler %s failed. It reported the following: %s" % (mangler.__name__, str(e))

        return args, kwargs
        

    def dispatch_events(self, handler_collection, method_name, *args, **kwargs):

        please_do_continue = True

        for handler in handler_collection.get(method_name, []):
            try:
                #pop off the instance information. We just want the function signature
                please_do_continue = handler(*args[1:], **kwargs)
                
                if please_do_continue == None:
                    please_do_continue = True

                if not please_do_continue:
                    break

            except Exception as e:
                print "Event listener %s failed. It reported the following: %s" % (handler.__name__, str(e))

        return please_do_continue

    
    for name, method in klass.__dict__.iteritems():

        if hasattr(method, "is_event"):

            setattr(klass, name, wrapper(method))
        
    setattr(klass, "_listeners", {})
    setattr(klass, "_interrogators", {})
    setattr(klass, "_manglers", {})
    setattr(klass, "attach_listener", attach_listener)
    setattr(klass, "attach_interrogator", attach_interrogator)
    setattr(klass, "attach_mangler", attach_mangler)
    setattr(klass, "dispatch_events", dispatch_events)
    setattr(klass, "run_manglers", run_manglers)

    return klass