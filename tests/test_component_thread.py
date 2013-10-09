
import unittest
import random
from pydesk import *

class child_comp(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.ev = Event(sim=self.sim)
	
	def main_thread(self):
		print "child_comp: main_thread started"
		print "child_comp: waiting time"
		yield wait_time,10
		print "child_comp: done waiting time"
		print "child_comp: emitting event"
		self.ev.emit()
		print "child_comp: done emitting event"

	def run(self):
		self.start( self.main_thread() )


class parent_comp(Component):

	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.child_inst = child_comp("child",self)
	
	def main_thread(self):
		print "parent_comp: Waiting for event from child"
		yield wait_event, self.child_inst.ev
		print "parent_comp: Done waitting event from child"
		print "parent_comp: Waiting for some time"
		yield wait_time, 10
		print "parent_comp: Done waiting for some time"
	
	def ev_cb(self):
		print "Ev has been emitted"

	def run(self):
		self.child_inst.ev.register_async_callback(self.ev_cb)
		self.start( self.main_thread() )

class top_module(Component):

	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.parent_inst = parent_comp("parent",self)


class ComponentThreadTest(unittest.TestCase):
	
	def testBasic(self):
		sim = Simulator()
		top_inst = top_module("top",sim)
		sim.simulate_comp()

		self.assertEqual(sim.time,20)

if __name__=='__main__':
	unittest.main()




