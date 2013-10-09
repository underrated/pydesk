'''
Created on Oct 9, 2013

@author: developer
'''
import unittest
from pydesk import *

class TestMutex(unittest.TestCase):


    def testMutex(me):
        my_mutex = Mutex()
        def thread1(sim):
            sim.message("thread1", "Just started")
            yield wait_time,10
            sim.message("thread1", "Grabbing lock")
            yield my_mutex.lock()
            sim.message("thread1", "Grabbed lock")
            yield wait_time,10
            sim.message("thread1", "Releasing lock")
            my_mutex.unlock()
        def thread2(sim):
            sim.message("thread2", "Just started")
            yield wait_time,15
            sim.message("thread2", "Grabbing lock")
            yield my_mutex.lock()
            sim.message("thread2", "Grabbed lock")
            yield wait_time,5
            sim.message("thread2", "Releasing")
            my_mutex.unlock()
        
        sim = Simulator()
        sim.register_thread(thread1(sim))
        sim.register_thread(thread2(sim))
        sim.simulate()
        self.assertEqual(sim.time, 20)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()