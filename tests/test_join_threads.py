'''
Created on Oct 1, 2013

@author: developer
'''
import unittest
from pydesk import *

class TestJoinThreads(unittest.TestCase):

    def testJoinAll(self):
        def main_thread(sim):
            sim.message("testJoinAll - Main Thread", "Starting threads")
            def thread1(sim):
                sim.message("Thread1","Start")
                yield wait_time,10
                sim.message("Thread1","End")
            def thread2(sim):
                sim.message("Thread2","Start")
                yield wait_time,20
                sim.message("Thread2","End")
            def thread3(sim):
                yield wait_time,1
                sim.message("Thread3","Start")
                yield wait_time,15
                sim.message("Thread3","End")
            sim.message("Main Thread", "Waiting for threads")
            yield join_all,thread1(sim),thread2(sim),thread3(sim)
            sim.message("Main Thread", "Threads finished")
        
        sim = Simulator()
        sim.register_thread(main_thread(sim))
        sim.simulate()
        self.assertEqual(sim.time, 20)
    
    def testJoinFirst(self):
        def main_thread(sim):
            sim.message("testJoinFirst - Main Thread", "Starting threads")
            def thread1(sim):
                sim.message("Thread1","Start")
                yield wait_time,10
                sim.message("Thread1","End")
            def thread2(sim):
                sim.message("Thread2","Start")
                yield wait_time,20
                sim.message("Thread2","End")
            def thread3(sim):
                yield wait_time,1
                sim.message("Thread3","Start")
                yield wait_time,15
                sim.message("Thread3","End")
            sim.message("Main Thread", "Waiting for threads")
            yield join_first,thread1(sim),thread2(sim),thread3(sim)
            sim.message("Main Thread", "Threads finished")
        
        sim = Simulator()
        sim.register_thread(main_thread(sim))
        sim.simulate()
        self.assertEqual(sim.time, 10)
    
    def testJoinAny(self):
        def main_thread(sim):
            sim.message("testJoinAny - Main Thread", "Starting threads")
            def thread1(sim):
                sim.message("Thread1","Start")
                yield wait_time,10
                sim.message("Thread1","End")
            def thread2(sim):
                sim.message("Thread2","Start")
                yield wait_time,20
                sim.message("Thread2","End")
            def thread3(sim):
                yield wait_time,1
                sim.message("Thread3","Start")
                yield wait_time,15
                sim.message("Thread3","End")
            sim.message("Main Thread", "Waiting for threads")
            yield join_any,\
                thread1(sim),\
                thread2(sim),\
                thread3(sim)
            sim.message("Main Thread", "Thread finished")
        
        sim = Simulator()
        sim.register_thread(main_thread(sim))
        sim.simulate()
        self.assertEqual(sim.time, 20)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()