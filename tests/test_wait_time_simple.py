
import unittest
import random
from pydesk import *

class WaitTimeTest(unittest.TestCase):

	def thread1(self,sim):
		print "wait_time_example - time="+str(sim.time) + " : a1"
		yield wait_time,1
		print "wait_time_example - time="+str(sim.time) + " : a2"
		yield wait_time,35
		print "wait_time_example - time="+str(sim.time) + " : a3"
		yield wait_time,100
		print "wait_time_example - time="+str(sim.time) + " : a4"
	
	def thread2(self,sim):
		print "wait_time_example - time="+str(sim.time) + " : b1"
		yield wait_time,3
		print "wait_time_example - time="+str(sim.time) + " : b2"
		yield wait_time,50
		print "wait_time_example - time="+str(sim.time) + " : b3"
		yield wait_time,200
		print "wait_time_example - time="+str(sim.time) + " : b4"
	
	def testWaits(self):
		sim = Simulator()
		sim.verbose=1
		sim.register_thread( self.thread1(sim) )
		sim.register_thread( self.thread2(sim) )
		#import pdb; pdb.set_trace()
		sim.simulate()
		self.assertEqual(sim.time,253)

#	def testSimultaneous(self):
#		def t1():
#			print "a1"
#			yield wait_time,10
#			print "a2"
#			yield wait_time,20
#			print "a3"
#		def t2():
#			print "b1"
#			yield wait_time,10
#			print "b2"
#			yield wait_time,20
#			print "b3"
#		sim = Simulator()
#		sim.verbose=1
#		sim.register_thread( t1() )
#		sim.register_thread( t2() )
#		sim.register_thread( t2() )
#		sim.register_thread( t2() )
#		sim.simulate()
#		self.assertEqual(sim.time,30)
#	
#	def testLoops(self):
#		def t1():
#			for i in range(3):
#				print "begin:a"+str(i)
#				yield wait_time,2
#				print "end:a"+str(i)
#		def t2():
#			for i in range(5):
#				print "begin:b"+str(i)
#				yield wait_time,3
#				print "end:b"+str(i)
#		sim = Simulator()
#		sim.verbose = 1
#		sim.register_thread( t1() )
#		sim.register_thread( t2() )
#		sim.simulate()
#		self.assertEqual(sim.time,15)
#	
#	def testRand(self):
#		def thread_random(sim,iters,times):
#			print "====== Starting thread with "+str(iters)+" iterations:"
#			for i in range(iters):
#				print "== time : "+str(sim.time)+" begin:iter "+str(i)+"/"+str(iters)
#				yield wait_time,times[i]
#				print "== time : "+str(sim.time)+" end:iter "+str(i)+"/"+str(iters)
#			print "====== Ending thread with "+str(iters)+" iterations at time "+str(sim.time)+"."
#
#		nof_threads = random.randint(2,5)
#		
#		sim = Simulator()
#		sim.verbose = 1
#		expected_time = 0
#		print "Generating %d threads : " % nof_threads
#		for i in range(nof_threads):
#			iters = random.choice([1,5,10,20,100])
#			times = [ random.randint(1,10) for _ in range(iters) ]
#			if sum(times) > expected_time:
#				expected_time=sum(times)
#			sim.register_thread( thread_random(sim,iters,times) )
#
#		sim.simulate()
#		print "Expected time = %d" % sim.time
#		self.assertEqual(sim.time,expected_time)


if __name__=='__main__':
	unittest.main()

