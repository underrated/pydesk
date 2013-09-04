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

	def on_clk_fall(self):
		pass
#		print "time:"+str(self.sim.time)+" Clock fall : Clock changed from "+str(self.clk.prev_value)+" to "+str(self.clk.value)

	def on_clk_change(self):
		pass
#		print "*SAMPLE* time:"+str(self.sim.time)+" clk:"+str(self.clk.value)+" in_s:"+str(self.in_s.value)+" self.out_s:"+str(self.out_s.value)
	
	def on_out_s_change(self):
		pass
#		print "time:"+str(self.sim.time)+" Output changed from "+str(self.out_s.prev_value)+" to "+str(self.out_s.value)

	def on_in_s_change(self):
		pass
#		print "time:"+str(self.sim.time)+" Input changed from "+str(self.in_s.prev_value)+" to "+str(self.in_s.value)

	def run(self):
		print "Setting up flip flop"
		self.clk.rise.register_sync_callback(self.on_clk)
		self.clk.fall.register_sync_callback(self.on_clk_fall)
		self.clk.change.register_sync_callback(self.on_clk_change)
		self.out_s.change.register_sync_callback(self.on_out_s_change)
		self.in_s.change.register_sync_callback(self.on_in_s_change)

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



