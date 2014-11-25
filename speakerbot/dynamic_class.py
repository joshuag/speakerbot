"""
    This falls into my "bad idea that I'm playing with" category. Withold judgement and ye lunches.

    Upgraded to plausible.
"""
from importlib import import_module

class Singleton(type):
    
    instance_list = {}
    
    def __call__(klass, *args, **kwargs):

        if not klass in klass.instance_list:
            klass.instance_list[klass] = super(Singleton, klass).__call__(*args, **kwargs)
        
        return klass.instance_list[klass]

class MissingPluginException(Exception):
    pass

class attach_methods(object):

    def __init__(self, *modules, **kwargs):

        self.methods = {}
        #allow installing the functions under a specific dictionary
        self.method_dict_name = kwargs.get("method_dict_name", None)
        self.filter_attribute = kwargs.get("filter_attribute", None)
        self.modules = modules
        self.methods = {}

    def __call__(self, klass):

        self.get_methods(klass)

        self.install_methods(klass)
        
        return klass

    def get_methods(self, klass):

        filter_attribute = getattr(klass, "filter_attribute", self.filter_attribute)

        for _module in self.modules:
            imported_module = import_module(_module)

            for method in dir(imported_module):
                resolved_method = getattr(imported_module, method)
                if (method[0:2] != "__" and not filter_attribute) or (filter_attribute and getattr(resolved_method, filter_attribute, False)):
                    self.methods[method] = resolved_method

    def install_methods(self, klass):
        
        method_dict_name = getattr(klass, "method_dict_name", self.method_dict_name)

        if method_dict_name:
            setattr(klass, method_dict_name, self.methods)
        else:
            for method in self.methods:
                setattr(klass, method, self.methods[method])


def plugin(func):
    def wrapped(*args, **kwargs):
        print "Executing " + func.__name__
        return func(*args, **kwargs)

    set_function_attribute(wrapped, "plugin", True)
    return wrapped

def set_function_attribute(func, name, value):
    setattr(func, name, value)


class PluggableObject(object):

    filter_attribute = "plugin"
    method_dict_name = "plugins"

    def __init__(self):
        pass

    def dispatch_plugin(self, name, *args, **kwargs):
        try:
            plugin = self.plugins[name]
        except KeyError:
            raise MissingPluginException("There is not a plugin installed for %s" % name)
        return plugin(self, *args, **kwargs)