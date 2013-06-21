import unittest
import random

from pydesk import *

class SelfThreadTest(unittest.TestCase):
	
	def thread1(self,sim):
		print "Getting pointer to self"
		self.bad_thread = yield sim_cmd,get_thread_self
		yield wait_event,self.dummy_ev
		print "What???"
	
	def thread2(self,sim):
		yield wait_time,10
		print "Killing bad thread"
		if self.bad_thread:
			sim.kill_thread_by_handle(self.bad_thread)
		print "Killed it"
	
	def testMain(self):
		# Initialize some variable
		self.bad_thread=None
		self.dummy_ev=Event()
		# Start simulation
		sim = Simulator()
		sim.register_thread(self.thread1(sim))
		sim.register_thread(self.thread2(sim))
		#import pdb; pdb.set_trace()
		sim.simulate()

if __name__=='__main__':
	unittest.main()

