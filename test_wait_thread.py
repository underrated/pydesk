
import unittest
import random
from pydesk import *

class WaitThreadTest(unittest.TestCase):

	def testBasic(self):
		def child_thread(sim):
			print "==child_thread started"
			yield wait_time,10
			print "==child_thread ended"
		def parent_thread(sim):
			print "====parent_thread started"
			print "====starting child_threads"
			yield wait_thread,child_thread(sim)
			yield wait_time,10
			yield wait_thread,child_thread(sim)
			print "====child_threads ended"
			print "====parent_thread ended"

		sim=Simulator()
		sim.register_thread( parent_thread(sim) )
		#import pdb; pdb.set_trace()
		sim.simulate()
		self.assertEqual(sim.time,30)
	
	def testRecursive(self):
		def recursive_thread(sim,n):
			if(n==3):
				print "Reached exit condition"
				yield wait_time,10
				print "Thread Finished"
			else:
				print "Reached n=%d" % n
				yield wait_thread,recursive_thread(sim,n+1)
				yield wait_time,10
			
			print "Thread Finished"

		sim=Simulator()
		sim.register_thread( recursive_thread(sim,0) )
		#import pdb; pdb.set_trace()
		sim.simulate()
		self.assertEqual(sim.time,40)


if __name__=='__main__':
	unittest.main()
