import inspect
import sys

#failed experiment

def install_prindent():
    sys.stdout = Prindent(sys.stdout)

class Prindent(sys.stdout):

    def __init__(self, streamlike, depth=len(inspect.stack())):

        super(Prindent, self).__init__()

        self.streamlike = streamlike

        self.depth = depth

    def indentation(self):

        from IPython import embed
        embed()

        return len(inspect.stack()) - self.depth

    def write(self, data):

        prefix  = '    ' * self.indentation()
        
        def indent(l):
            if l:
                return prefix + l
            else:
                return l

        data = '\n'.join([indent(line) for line in data.split('\n')])
        
        self.streamlike.write(data)

install_prindent()