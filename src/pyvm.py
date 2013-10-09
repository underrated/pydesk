from pydesk import *

class pyvm_seq_item:
    def __init__(self):
        self.prio = 0
        self.driving_sequence = None
        self.item_id = 0
    
class pyvm_sequence(pyvm_seq_item):
    def __init__(self):
        pyvm_seq_item.__init__(self)
        self.sequencer = None
    
    def body(self):
        pass
    
    def start(self,sqr):
        pass

class pyvm_sequencer(Component):
    def __init__(self,name,parent):
        Component.__init__(self,name,parent)
    
    
    
    
    

