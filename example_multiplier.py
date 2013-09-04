from pydesk import *


class shift_add_multiplier(Component):
    def __init__(self,name, parent):
        Component.__init__(self, name, parent)
        # Inputs
        self.i_clk = state_variable(0, "i_clk", self)
        self.i_clk.bit_size = 1
        self.i_reset = state_variable(0, "i_reset", self)
        self.i_reset.bit_size = 1
        self.i_op1 = state_variable(0, "i_op1", self)
        self.i_op1.bit_size = 16
        self.i_op2 = state_variable(0, "i_op2", self)
        self.i_op2.bit_size = 4
        self.i_valid = state_variable(0, "i_valid", self)
        self.i_valid.bit_size = 1
        # Outputs
        self.o_result = state_variable(0,"o_result",self)
        self.o_result.bit_size = 20
        self.o_valid = state_variable(0,"o_valid", self)
        self.o_valid.bit_size = 1
        self.o_busy = state_variable(0, "o_busy", self)
        self.o_busy.bit_size = 1
        # Internal signals and registers
        self.s_op1 = state_variable(0, "s_op1", self)
        self.s_op1.bit_size = 20
        self.s_op2 = state_variable(0, "s_op2", self)
        self.s_op2.bit_size = 4
        self.s_result = state_variable(0, "s_result", self)
        self.s_result.bit_size = 20
        self.s_add = state_variable(0, "s_add", self)
        self.s_add.bit_size = 1
        self.s_busy = state_variable(0, "s_busy", self)
        self.s_busy.bit_size = 1
        
        # Assigns 
        self.s_add.assign_expr(lambda args : args[0].value & 1, [self.s_op2])
    
    # Input sampling 
    def sample_inputs(self): 
        if(self.i_valid.value==1):
            self.s_op1 <= self.i_op1.value
            self.s_op2 <= self.i_op2.value
            self.s_busy <= 1
    
    # Busy signal logic
    def busy_handler(self):
        if self.i_reset.value==1:
            self.o_busy <=0
        else:    
            self.o_busy <= self.s_busy.value
    
    # Shift-add algorithm
    def shift_add(self):
        if(self.i_reset.value==1):
            self.s_op1 <=0
            self.s_op2 <=0
            self.s_result <=0
            self.o_valid <=0
        else:
            if(self.s_busy.value==1):
                if(self.s_add.value==1 ):
                    self.s_result <= (self.s_result.value+self.s_op1.value) & 0xFFFFF
                self.s_op1 <= (self.s_op1.value << 1) & 0xFFFFF
                self.s_op2 <= (self.s_op2.value >> 1) & 0xF
                if(self.s_op2.value == 0):
                    self.s_busy <= 0
                    self.o_result <= self.s_result.value
                    self.o_valid <= 1
            else:
                self.o_valid <= 0
                self.o_result <= 0
    
    def run(self):
        self.i_clk.rise.register_sync_callback(self.sample_inputs)
        self.i_clk.rise.register_sync_callback(self.busy_handler)
        self.i_clk.rise.register_sync_callback(self.shift_add)


class mult_tb(Component):
    def __init__(self,name,parent):
        Component.__init__(self, name, parent)
        self.mult_inst = shift_add_multiplier("mult_inst",self)
        self.clk_thread = None
    
    def drive_clk(self):
        self.clk_thread = yield sim_cmd,get_thread_self
        self.mult_inst.i_clk.value = 1
        while True:
            yield wait_time,5
            self.mult_inst.i_clk.value = int(not self.mult_inst.i_clk.value)
    
    def drive_data(self):
        self.mult_inst.i_reset.value = 0
        for i in range(2):
            yield wait_event, self.mult_inst.i_clk.rise
        self.mult_inst.i_reset.value = 1
        for i in range(2):
            yield wait_event, self.mult_inst.i_clk.rise
        self.mult_inst.i_reset.value = 0
        for i in range(2):
            yield wait_event, self.mult_inst.i_clk.rise
        self.mult_inst.i_valid.value = 1
        self.mult_inst.i_op1.value = 137
        self.mult_inst.i_op2.value = 3
        yield wait_event,self.mult_inst.i_clk.rise
        self.mult_inst.i_valid.value = 0
        self.mult_inst.i_op1.value = 0
        self.mult_inst.i_op2.value = 0
        for i in range(10):
            yield wait_event, self.mult_inst.i_clk.rise
        # End simulation
        self.kill_thread(self.clk_thread)
        
    def run(self):
        print "Setting up tb"
        self.start(self.drive_clk())
        self.start(self.drive_data())


sim = Simulator()
top = mult_tb("top",sim)
#import pdb; pdb.set_trace()
sim.simulate_comp()
vcd_h = vcd_handler(sim,"result.vcd")
vcd_h.write_vcd()   
          
            