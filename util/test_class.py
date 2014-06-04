import prindent

class Foo():
	
	def __init__(self):
		print "level 1"

	def indent(self):
		print "level 1"
		if True:
			print "level 2"
		self.foo()

	def foo(self):
		print "level 2"
		self.bar()

	def bar(self):
		print "level 3"

a = Foo()