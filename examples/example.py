
from pydesk import *

b = 0

my_event1 = Event()
my_event2 = Event()

def thread1():
	global b
	while True:  # FIXME : doesn't run forever
		if b == 0:
			b = 1
			print "0 -> 1"
			my_event1.emit()
			yield wait_time, 1
		yield wait_event, my_event2
	

def thread2():
	global b
	while True:
		if b == 1:
			b = 0
			print "1 -> 0"
			my_event2.emit()
			yield wait_time, 1
		yield wait_event, my_event1
	
sim = Simulator()
sim.register_thread(thread1())
sim.register_thread(thread2())

sim.simulate()
