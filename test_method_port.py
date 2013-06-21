
import unittest
import random

from pydesk import *

class Producer:
	def __init__(self):
		self.out = out_method_port("out")

	def do_something(self):
		print "Doing something"
		self.out.transfer_nb("Hello")

class Consumer:
	def in_mp_imp(self,s):
		print "Received "+s
		self.touched = True

	def __init__(self):
		self.in_mp = in_method_port("in",self.in_mp_imp)
		self.touched = False

class MethodPortTestNB(unittest.TestCase):
	
	def testPorts(self):
		prod = Producer()
		cons = Consumer()
		prod.out.connect(cons.in_mp)

		prod.do_something()

		self.assertEqual(cons.touched,True)


class MethodPortTestB(unittest.TestCase):
	
	def thread_with_ports(self):
		out_p = out_method_port("out_p")
		def my_thread(s):
			print "Step 1 "+s
			yield wait_time, 10
			print "Step 2 "+s
		in_p = in_method_port("in_p",my_thread)
		
		out_p.connect(in_p)

		yield wait_thread, out_p.transfer_b("Hello")

	def testPorts(self):
		sim = Simulator()
		sim.register_thread( self.thread_with_ports() )
		sim.simulate()
		self.assertEqual(sim.time,10)


if __name__=='__main__':
	unittest.main()


