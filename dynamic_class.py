"""
    This falls into my "bad idea that I'm playing with" category. Withold judgement and ye lunches.

"""
from importlib import import_module
class attach_methods(object):

    def __init__(self, *modules, **kwargs):

        self.methods = {}
        #allow installing the functions under
        self.klass_dict_name = kwargs.get("klass_dict_name", None)
        print modules
        for _module in modules:
            imported_module = import_module(_module)

            for method in dir(imported_module):
                if method[0:2] != "__":
                    self.methods[method] = getattr(imported_module, method)

    def __call__(self, klass):

        self.install_methods(klass)
        
        return klass

    def install_methods(self, klass):
        
        if self.klass_dict_name:
            setattr(klass, self.klass_dict_name, self.methods)
        else:
            for method in self.methods:

                if not self.klass_dict_name:
                    setattr(klass, method, self.methods[method])


