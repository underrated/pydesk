'''
Created on Oct 10, 2013

@author: developer
'''
import unittest
from pydesk import *

class TestErrWrn(unittest.TestCase):

    def testErr(self):
        sim = Simulator()
        def thread1(sim):
            sim.message("COOL_MSG","Starting thread1")
            sim.warning("COOL_WRN","Warning thread1 started...")
            yield wait_time,10
            yield sim.error("BAD_ERR", "Something bad has happened")
            sim.warning("WHAT???","You shouldn't be reading this")
        sim.register_thread(thread1(sim))
        sim.simulate()
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()