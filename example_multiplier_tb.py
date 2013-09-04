from pydesk import *
from example_multiplier import shift_add_multiplier

class mult_input_item:    
    def __init__(self):
        self.op1, self.op2 = 0
        self.item_delay = 4
        self.item_delay_after = 0
        self.watch_busy = 1

class mult_in_if(Component):
    def __init__(self,name,parent):
        Component.__init__(self, name, parent)
        self.clk = state_variable(0,"clk",self)
        self.clk.bit_size = 1 
        self.op1 = state_variable(0,"op1",self)
        self.op1.bit_size = 16
        self.op2 = state_variable(0,"op2",self)
        self.op2.bit_size = 4
        self.valid = state_variable(0,"valid",self)
        self.valid.bit_size = 1
        self.busy = state_variable(0,"busy",self)
        self.busy.bit_size = 1

class mult_in_driver(Component):
    def __init__(self,name,parent):
        Component.__init__(self, name, parent)
        self.vif = mult_in_if("vif",self)
        self.clk_rise = self.vif.clk.rise
    
    def reset_if(self):
        self.vif.op1.value = 0
        self.vif.op2.value = 0
        self.vif.valid.value = 0
    
    def drive_item(self,item):
        for i in range(item.item_delay):
            yield wait_event, self.clk_rise
        if(item.watch_busy):
            while self.vif.busy.value==1:
                yield wait_event, self.clk_rise
        self.vif.op1.value = item.op1
        self.vif.op2.value = item.op2
        self.vif.valid.value = 1
        yield wait_event, self.clk_rise
        self.reset_if()
        for i in range(item.item_delay_after):
            yield wait_event, self.clk_rise
        

class mult_in_monitor(Component):
    pass

class mult_in_agent(Component):
    pass

class mult_out_monitor(Component):
    pass

class mult_out_agent(Component):
    pass

class reset_driver(Component):
    pass

class reset_monitor(Component):
    pass

class reset_agent(Component):
    pass

class sam_env(Component):
    pass

class basic_test(Component):
    pass 

class top_module(Component):
    pass

sim = Simulator("sim")
top_inst = top_module("top_module",sim)
sim.simulate_comp()
vcd_h = vcd_handler(sim,"result.vcd")
vcd_h.write_vcd()