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
		
class ff_tb(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.ff = flip_flop("ff",self)
		self.clk_thread = None
	
	def drive_clk(self):
		self.clk_thread = yield sim_cmd,get_thread_self
		self.ff.clk.value = 1
		while True:
			#print "Old clock is "+str(self.ff.clk.value)
			yield wait_time,5
			self.ff.clk.value = int(not self.ff.clk.value)
			#print "New clock should be "+str(self.ff.clk.value^1)
			#print "New actually is "+str(self.ff.clk.value^1)

	def drive_signals(self):
		self.ff.in_s.value= 0
		for i in range(3): yield wait_event, self.ff.clk.rise
		self.ff.in_s.value = 1
		for i in range(3): yield wait_event, self.ff.clk.rise
		self.ff.in_s.value = 0
		for i in range(2): yield wait_event, self.ff.clk.rise
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
vcd_h = vcd_handler(sim,"result.vcd")
vcd_h.write_vcd()



