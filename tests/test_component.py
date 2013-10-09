
import unittest
import random
from pydesk import *

class comp2(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
	
	def run(self):
		print "Hello from comp2"


class comp1(Component):

	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.c2_inst = comp2("c2",self)

	def run(self):
		print "Hello from comp1"

class top_module(Component):

	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.c1_inst1 = comp1("c1_1",self)
		self.c1_inst2 = comp1("c1_2",self)


class ComponentTest(unittest.TestCase):
	
	def testBasic(self):
		sim = Simulator()
		top_inst = top_module("top",sim)

		sim.initialize()


if __name__=='__main__':
	unittest.main()



