'''
Created on Sep 19, 2013

@author: developer
'''

from pydesk import *

class Test(Component):
    def __init__(self,name,parent):
        Component.__init__(self, name, parent)
        self.ev1 = Event(sim=self.sim)
        self.ev2 = Event(sim=self.sim)
        
        self.ev3 = self.te([self.ev1,10,(2,self.ev2),5,self.ev1])
    
    
    def ev3_cb(self):
        self.sim.message("It happened")
        
    def main_thread(self):
        yield wait_time,10
        
        self.ev1.emit()
        yield wait_time,10
        self.ev2.emit()
        yield wait_time,1
        self.ev2.emit()
        yield wait_time,5
        self.ev1.emit()
        
        yield wait_time,30
        
    def run(self):
        self.ev3.register_sync_callback(self.ev3_cb)
        self.start(self.main_thread())
        
sim=Simulator()
test = Test("test",sim)
sim.simulate_comp()


    
    
        