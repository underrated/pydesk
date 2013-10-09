
import unittest
import random

from pydesk import *

class WaitEventTest(unittest.TestCase):
		
	def testBasic(self):

		self.done=False
		sim=Simulator()
		self.ev = Event(sim=sim)
		self.ev2 = Event(sim=sim)
		
		def thread1(sim):
			print "Emitting event"
			self.ev.emit()
			yield wait_time,10
			print "Thread1 finished"

		def thread2(sim):
			print "Waiting for event"
			yield wait_event,self.ev
			self.done = True
			print "Event emitted , thread2 finished"
		def ev_cb():
			print "ev_cb: Ev has been emitted"
			self.ev2.emit()
		def ev2_cb():
			print "ev2_cb: Ev2 has been emitted"

		self.ev.register_async_callback(ev_cb)
		self.ev2.register_async_callback(ev2_cb)

		sim.register_thread( thread1(sim) )
		sim.register_thread( thread2(sim) )
		sim.register_thread( thread2(sim) )
		#import pdb; pdb.set_trace()
		sim.simulate()
		self.assertEqual(sim.time,10)
		self.assertEqual(self.done,True)

	def testLoops(self):
		sim=Simulator()
		self.ev = Event(sim=sim)
		self.done = False
		def thread1(sim):
			print "Thread1 started"
			while True:
				self.ev.emit()
				yield wait_time,1

		def thread2(sim,iters):
			for i in range(iters):
				print "Waiting event iter %d" % i
				yield wait_event,self.ev
				print "Received event iter %d" % i
			print "Killing thread1"
			sim.kill_thread_by_type("thread1")
			self.done=True
			print "Thread2 DONE."
			
		def ev_cb():
			print "ev_cb: Ev emitted"

		self.ev.register_async_callback(ev_cb)

		sim.register_thread( thread1(sim) )
		iters = random.randint(3,10)
		sim.register_thread( thread2(sim,iters) )
		#import pdb; pdb.set_trace()
		sim.simulate()
		self.assertEqual(sim.time,iters)
		self.assertEqual(self.done,True)

	def testLateWait(self): 
		
		# If a thread consumes an event at an earlier time then
		# other threads waiting for that even at later times
		# won't see it emitted
		# TODO is it correct to be like this???

		self.done=False
		sim = Simulator()
		self.ev = Event(sim=sim)
		self.ev2 = Event(sim=sim)
		
		def thread1(sim):
			print "TLW : Emitting event"
			yield wait_time,5
			self.ev.emit()
			yield wait_time,10
			print "TLW : Thread1 finished"

		def thread2(sim):
			print "TLW2 : Waiting for event"
			yield wait_time,6
			yield wait_event,self.ev
			self.done = True
			print "TLW2 : Event emitted , thread2 finished"	

		def thread3(sim):
			print "TLW3 : Waiting for event"
			yield wait_time,7
			yield wait_event,self.ev
			self.done = True
			print "TLW3 : Event emitted , thread2 finished"	


		sim.register_thread(thread1(sim))
		sim.register_thread(thread2(sim))
		sim.register_thread(thread3(sim))

		# sim.simulate() # This simulation gets stuck in a deadlock
	
	def testSyncCallbacks(self):
		pass
		

if __name__=='__main__':
	unittest.main()

