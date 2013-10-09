from pydesk import *

class flip_flop(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.clk = state_variable(0,"clk",self)
		self.clk.bit_size = 1
		# self.clk.first_value = 1
		# self.clk.prev_value = 1
		self.in_s = state_variable(0,"in_s",self)
		self.in_s.bit_size = 1
		self.out_s = state_variable(0,"out_s",self)
		self.out_s.bit_size = 1

	def on_clk(self):
		self.out_s <= self.in_s.value

	def run(self):
		print "Setting up flip flop"
		self.clk.rise.register_sync_callback(self.on_clk)

class shift_reg(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		# Declare flip flips and clk
		self.clk = state_variable(0,"clk",self)
		self.clk.bit_size = 1
		self.in_s = state_variable(0,"in_s",self)
		self.in_s.bit_size = 1
		self.ff_1 = flip_flop("ff_1",self)	
		self.ff_1.bit_size = 1	
		self.ff_2 = flip_flop("ff_2",self)	
		self.ff_2.bit_size = 1
		self.ff_3 = flip_flop("ff_3",self)	
		self.ff_3.bit_size = 1
		self.ff_4 = flip_flop("ff_4",self)	
		self.ff_4.bit_size = 1
		# Make clock connections
		self.clk.connect(self.ff_1.clk)
		self.clk.connect(self.ff_2.clk)
		self.clk.connect(self.ff_3.clk)
		self.clk.connect(self.ff_4.clk)
		# Make flip flop connections
		self.in_s.connect(self.ff_1.in_s)
		#self.ff_2.in_s.assign_expr(lambda args:args[0].value,[self.ff_1.out_s])
		#self.ff_3.in_s.assign_expr(lambda args:args[0].value,[self.ff_2.out_s])
		#self.ff_4.in_s.assign_expr(lambda args:args[0].value,[self.ff_3.out_s])
		self.ff_1.out_s.connect(self.ff_2.in_s)
		self.ff_2.out_s.connect(self.ff_3.in_s)
		self.ff_3.out_s.connect(self.ff_4.in_s)
	
			
class ff_tb(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.sr = shift_reg("sr",self)
		self.clk_thread = None
	
	def drive_clk(self):
		self.clk_thread = yield sim_cmd,get_thread_self
		self.sr.clk.value = 1
		while True:
			#print "Old clock is "+str(self.ff.clk.value)
			yield wait_time,5
			self.sr.clk.value = int(not self.sr.clk.value)
			#print "New clock should be "+str(self.ff.clk.value^1)
			#print "New actually is "+str(self.ff.clk.value^1)
	
	def drive_signals(self):
		self.sr.in_s.value= 0
		for i in range(3): yield wait_event, self.sr.clk.rise
		self.sr.in_s.value = 1
		for i in range(3): yield wait_event, self.sr.clk.rise
		self.sr.in_s.value = 0
		for i in range(5): yield wait_event, self.sr.clk.rise
		self.kill_thread(self.clk_thread)
	
	def run(self):
		print "Setting up tb"
		# TODO : The order in which they are started matters - it shouldn't
		self.start(self.drive_clk())
		self.start(self.drive_signals())

sim = Simulator()
top = ff_tb("top",sim)
#import pdb; pdb.set_trace()
sim.simulate_comp()
vcd_h = vcd_handler(sim,"result_sr.vcd")
vcd_h.write_vcd()

