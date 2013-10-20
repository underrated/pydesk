import unittest
import random

from pydesk import *

class TempExprTest(unittest.TestCase):
        
    def testOrder(self):
        def thread1(sim):
            sim.message("thread1","Emitting ev1")
            self.ev1.emit()
            sim.message("thread1","Waiting 10 tus")
            yield wait_time,10
            sim.message("thread1","Emitting ev2")
            self.ev2.emit()
            sim.message("thread1","Waiting 10 tus")
            yield wait_time,10
        
        def thread2(sim):
            sim.message("thread2","Waiting for ev3")
            yield wait_event,self.ev3
            sim.message("thread2","Received ev3")
            sim.message("thread2","Waiting 20 tus")
            yield wait_time,20
            sim.message("thread2","EOS")
        
        sim = Simulator()
        self.ev1 = Event("ev1",sim)
        self.ev2 = Event("ev2",sim)
        self.ev3 = self.ev1>>self.ev2
        sim.register_thread(thread1(sim))
        sim.register_thread(thread2(sim))
        sim.simulate()
        self.assertEqual(sim.time, 30)
        
    def testOr(self):
        def thread1(sim):
            sim.message("thread1","Emitting ev1")
            self.ev1.emit()
            sim.message("thread1","Waiting 10 tus")
            yield wait_time,10
            sim.message("thread1","Emitting ev2")
            self.ev2.emit()
            sim.message("thread1","Waiting 10 tus")
            yield wait_time,10
        
        def thread2(sim):
            sim.message("thread2","Waiting for ev3")
            yield wait_event,self.ev3
            sim.message("thread2","Received ev3")
            sim.message("thread2","Waiting 20 tus")
            yield wait_time,20
            sim.message("thread2","EOS")
        def ev4_cb():
            sim.message("ev4_cb","ev4 has been emitted")
        
        sim = Simulator()
        self.ev1 = Event("ev1",sim)
        self.ev2 = Event("ev2",sim)
        self.ev3 = self.ev1 | self.ev2
        self.ev4 = (self.ev1 | self.ev3)>>self.ev2
        self.ev4.register_sync_callback(ev4_cb)
        sim.register_thread(thread1(sim))
        sim.register_thread(thread2(sim))
        sim.simulate()
        self.assertEqual(sim.time, 20)
        
    def testAnd(self):
        def thread1(sim):
            sim.message("thread1","Emitting ev1")
            self.ev1.emit()
            sim.message("thread1","Emitting ev2")
            self.ev2.emit()
            sim.message("thread1","Waiting 10 tus")
            yield wait_time,10
            sim.message("thread1","Done 10 tus")
        
        def thread2(sim):
            sim.message("thread2","Waiting for ev3")
            yield wait_event,self.ev3
            sim.message("thread2","Received ev3")
            sim.message("thread2","Waiting 20 tus")
            yield wait_time,20
            sim.message("thread2","EOS")
        
        sim = Simulator()
        self.ev1 = Event("ev1",sim)
        self.ev2 = Event("ev2",sim)
        self.ev3 = self.ev1 & self.ev2
        sim.register_thread(thread1(sim))
        sim.register_thread(thread2(sim))
        sim.simulate()
        self.assertEqual(sim.time, 20)
        
    def testRepeat(self):
        def thread1(sim):
            for i in range(5):
                sim.message("thread1","i={0}".format(i))
                sim.message("thread1","Emitting ev1")
                self.ev1.emit()
                sim.message("thread1","Waiting 10 tus")
                yield wait_time,10
            sim.message("thread1","EOS")
        
        def thread2(sim):
            sim.message("thread2","Waiting for ev2")
            yield wait_event,self.ev2
            sim.message("thread2","Received ev2")
            sim.message("thread2","Waiting 20 tus")
            yield wait_time,20
            sim.message("thread2","EOS")
        
        sim = Simulator()
        self.ev1 = Event("ev1",sim)
        self.ev2 = 3*self.ev1
        sim.register_thread(thread1(sim))
        sim.register_thread(thread2(sim))
        sim.simulate()
        self.assertEqual(sim.time, 50)
        
        
if __name__=='__main__':
    unittest.main()

