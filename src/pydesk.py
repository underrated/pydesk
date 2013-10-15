from constants import *
import threading
import time
from types import *

# Simulator - this is where everything is happening
class Simulator:
	def __init__(self):
		self.components = { }
		self.threads = [ ]
		self.times_to_wait = { }
		self.events_to_wait = { }
		self.emitted_events = [ ]
		self.events_to_fire = [ ]
		self.threads_to_wait = { }
		self.threads_to_join = { }
		self.thread_names = { }
		self.thread_states = { }
		self.thread_components = { }
		self.thread_parents = { }
		self.state_variables = []
		self.time = 0
		self.delta = 0 
		self.thread_counter = 0
		self.verbose = 0
		self.scheduled_assignments = { }
		self.sim_lock = threading.Lock()
		self.time_unit = (1,sim_seconds)
		self.verbosity = NONE
		self.current_thread = None
		self.disabled_messages = []
		self.disabled_errors = []
		self.disabled_warnings = []
	
	# Resume all threads that are scheduled to run
	def evaluate(self):
		if self.verbose: print "==============evaluate(time="+str(self.time)+"):"
		if self.verbose: print "==Old thread states:"
		if self.verbose: print self.thread_states
		if self.verbose: print "==Old times to wait:"
		if self.verbose: print self.times_to_wait
		if self.verbose: print "==="
		# Trigger sync callbacks for emitted events
		for e in self.events_to_fire:
			e.run_sync_callbacks()
		self.events_to_fire[:] = []
		# Resume threads waiting for time or events
		for t in self.threads:
			# If thread was killed close it
			if self.thread_states[t]==thread_finished:
				self.remove_thread(t)
				continue
			elif self.thread_states[t]==thread_running:
				state = self.resume_thread(t)
				if(state[0]==sim_cmd):
					while(state[0]==sim_cmd):
						state = self.process_cmd(state,t)
				# If thread is waiting for time or event or another thread then update the wait dictionaries
				if state[0]==wait_time:
					self.thread_states[t]=thread_waiting_time
					self.times_to_wait[t] = state[1]
				elif state[0] == wait_event:
					self.thread_states[t]=thread_waiting_event
					self.events_to_wait[t] = state[1]
					self.events_to_wait[t].add_listener()
				elif state[0]==wait_thread:
					self.thread_states[t]=thread_waiting_thread
					self.threads_to_wait[t] = state[1]
					self.register_thread(state[1],t)
				elif state[0] in (join_all,join_first,join_any):
					self.thread_states[t]="thread_"+state[0]
					self.threads_to_join[t] = state # TODO : check
					for jt in state[1:]:
						self.register_thread(jt, t)
				elif state==stop_simulation:
					return end_of_simulation
		#if thread_finished in self.thread_states.values():
		#	self.threads = [ it for it in self.threads if self.thread_states[it]!=thread_finished ]

		if self.verbose: print "==="
		if self.verbose: print "==New thread states:"
		if self.verbose: print self.thread_states
		if self.verbose: print "==New times to wait:"
		if self.verbose: print self.times_to_wait
		
		return continue_simulation
	# Resume a thread
	def resume_thread(self,t):
		state=None
		try:
			self.current_thread = t
			state=t.next()
		except StopIteration:
			if self.verbose: print "==Thread stopped:"+self.thread_names[t]
			self.remove_thread(t)
			state=None,None
		return state
	# Process a simulator command
	def process_cmd(self,query,t):
		state=None
		if query[1]==get_thread_self:
			try: state=t.send(t)
			except:	pass
		elif query[1]==get_children_threads:
			ctl=filter(lambda x:self.thread_parents[x]==t,self.thread_parents.keys())
			try: state=t.send(ctl)
			except: pass
		elif query[1]==start_thread:
			if t in self.thread_components.keys():
				self.register_component_thread(self.thread_components[t],query[2],t)
			else:
				self.register_thread(query[2],t)
		return state
	
	# Update simulation state
	def update(self,time_limit=-1):
		if self.verbose: print "==============update:"
		# Execute scheduled assignments
		for sv,val in self.scheduled_assignments.items():
			sv.do_assign(val)
			del self.scheduled_assignments[sv]
		for sv in self.state_variables:
			sv.do_update()
		
	# Update threads waiting for time
	def advance_time(self,time_limit=-1):
		self.delta=0
		#min_time=0
		min_time=min(self.times_to_wait.values())
		for t,wt in self.times_to_wait.items():
			if(wt==min_time and self.thread_states[t]!=thread_finished):
				self.thread_states[t]=thread_running
				del self.times_to_wait[t]
			else:
				if(self.time+min_time<time_limit or time_limit==-1):
					self.times_to_wait[t]-=min_time
				else:
					self.times_to_wait[t]-=(self.time+min_time)-time_limit
		# Update time
		if(time_limit==-1):
			if self.verbose: print "==min_time=%d" %min_time
			self.time += min_time
			if self.verbose: print "==global time=%d" %self.time
			return continue_simulation
		elif(self.time+min_time>=time_limit):
			self.time = time_limit
			return end_of_time

	# Update threads waiting for events
	def advance_delta(self,delta_limit=-1):	
		# Events to sync
		for t,e in self.events_to_wait.items():
			if e.state == event_on and self.thread_states[t]!=thread_finished:
				self.thread_states[t]=thread_running
				e.consume()
				del self.events_to_wait[t]
		# Schedule execution of sync callbacks	
		self.events_to_fire = self.emitted_events[:]
		# Clear list of emitted events for the next delta cycle
		self.emitted_events[:] = []
		# Advance delta counter
		if(self.delta+1>=delta_limit and delta_limit!=-1):
			self.delta = delta_limit
			return delta_limit_reached
		else:
			self.delta += 1

		if self.verbose: print "==="
		if self.verbose: print "==New thread states:"
		if self.verbose: print self.thread_states
		if self.verbose: print "==New times to wait:" 
		if self.verbose: print self.times_to_wait
		return continue_simulation
	
	# Update threads waiting for other threads to finish
	def advance_waiting_threads(self):
		for t,tw in self.threads_to_wait.items():
			if(self.thread_states[tw]==thread_finished and self.thread_states[t]!=thread_finished):
				self.thread_states[t]=thread_running
				del self.threads_to_wait[t]
		for t,state in self.threads_to_join.items():
			finished_threads = map(lambda x:self.thread_states[x]==thread_finished,state[1:])
			if state[0]==join_all:
				resume_condition = reduce(lambda x,y:x and y, finished_threads)
				if resume_condition:
					self.thread_states[t]=thread_running
					del self.threads_to_join[t]
			elif state[0]==join_first:
				resume_condition = reduce(lambda x,y:x or y,finished_threads)
				if resume_condition:
					self.thread_states[t] = thread_running
					for ct in state[1:]:
						if self.thread_states[ct]!=thread_finished:
							self.kill_thread_by_handle(ct)
					del self.threads_to_join[t]		
			elif state[0]==join_any:
				resume_condition = reduce(lambda x,y:x or y,finished_threads)
				if resume_condition:
					self.thread_states[t] = thread_running
					del self.threads_to_join[t]
			else:
				pass # crash with ugly horrific error
		return continue_simulation

	# Run a simulation
	def simulate(self,time_limit=-1,delta_limit=-1):
		sim_state = continue_simulation
		while True:
			sim_state = self.evaluate()
			if sim_state == end_of_simulation: break
			
			self.update()
			
			if(len(self.threads_to_wait)!=0 or len(self.threads_to_join)!=0):
				sim_state=self.advance_waiting_threads()
			
			if(len(self.emitted_events)!=0):
				sim_state = self.advance_delta(delta_limit)
				if sim_state==continue_simulation: continue
				else: return sim_state
			elif thread_running in self.thread_states.values():
				continue
			elif(len(self.times_to_wait)!=0):
				sim_state = self.advance_time(time_limit)
				if sim_state==continue_simulation: continue
				else: return sim_state
			else:
				break
		return end_of_simulation


	# Run a simulation with components
	def simulate_comp(self,time_limit=-1,delta_limit=-1):
		self.initialize()
		return self.simulate(time_limit,delta_limit)
	
	# Recursively call the run method of all the sub-components of root
	def run(self,root):
		root.run()
		if root.has_children():
			for c in root.get_children():
				self.run(c)

	# Find all the root components and recursively call the run methods of their children
	def initialize(self):
		roots = filter(lambda x:self.components[x]==None,self.components.keys())
		for r in roots:
			self.run(r)

	def schedule_assignment(self,sv,val):
		self.scheduled_assignments[sv]=val

	def register_component_thread(self,comp,t,parent_thread=None):
		self.threads.append(t)
		self.thread_components[t] = comp
		self.thread_states[t] = thread_running
		self.thread_names[t]=t.__name__+'_'+str(self.thread_counter)
		self.thread_counter+=1
		self.thread_parents[t]=parent_thread
		return t

	def register_thread(self,t,parent_thread=None):
		self.threads.append(t)
		self.thread_states[t] = thread_running
		self.thread_names[t]=t.__name__+'_'+str(self.thread_counter)
		self.thread_counter+=1
		self.thread_parents[t]=parent_thread
		return t
	
	def register_component(self,comp):
		self.components[comp]=comp.parent
	
	def kill_thread_by_handle(self,t):
		self.thread_states[t]=thread_finished
		ctl = filter(lambda x:self.thread_parents[x]==t,self.thread_parents.keys())
		for c in ctl:
			self.kill_thread_by_handle(c)
	
	def kill_thread_by_name(self,tn):
		if tn in self.thread_names.values():
			th = filter(lambda x:self.thread_names[x]==tn,self.thread_names.keys())
			self.kill_thread_by_handle(th)
	
	def kill_thread_by_type(self,tt):
		for t in self.threads:
			if t.__name__==tt:
				self.kill_thread_by_handle(t)
	
	def remove_thread(self,t):
		self.thread_states[t]=thread_finished
		try: del self.times_to_wait[t]
		except: pass				
		try: del self.events_to_wait[t]
		except: pass
		try: del self.threads_to_wait[t]
		except: pass
		try: del self.thread_parents[t]
		except: pass
	
	def wait_time(self,t,unit):
		at = t*(unit/self.time_unit[1])
		return (wait_time,at)
	
	def message(self,msg_id,msg,verb=NONE):
		if verb<=self.verbosity and msg_id not in self.disabled_messages:
			print "MESSAGE [{0}]-> {1}: {2}".format(self.time, msg_id, msg)
	
	def warning(self,wrn_id,wrn_msg):
		if wrn_id not in self.disabled_warnings:
			print "WARNING [{0}]-> {1}: {2}".format(self.time, wrn_id, wrn_msg)
	
	def error(self,err_id,err_msg):
		if err_id not in self.disabled_errors:
			print "ERROR [{0}]-> {1}: {2}".format(self.time, err_id, err_msg)
		return stop_simulation

# VCD handling inspired by MyHDL
codechars = ""
for i in range(33, 127):
	codechars += chr(i)
mod = len(codechars)

def gen_name_code():
	n = 0
	while 1:
		yield namecode(n)
		n += 1

def namecode(n):
	q, r = divmod(n, mod)
	code = codechars[r]
	while q > 0:
		q, r = divmod(q, mod)
		code = codechars[r] + code
	return code


class vcd_handler:
	def __init__(self,simulator,fname):
		self.sim=simulator
		self.timescale="1ps"
		self.f = open(fname,"w")
		self.namegen = gen_name_code()
	
	# Taken from MyHDL
	def int2bitstring(self,num):
		if num == 0:
			return '0'
		if abs(num) == 1:
			return '1'
		bits = []
		p, q = divmod(num, 2)
		bits.append(str(q))
		while not (abs(p) == 1):
			p, q = divmod(p, 2)
			#print "p=%d" % p
			bits.append(str(q))
		bits.append('1')
		bits.reverse()
		return ''.join(bits)


	def bin(self,num, width=0):
		"""Return a binary string representation.

		num -- number to convert
		Optional parameter:
		width -- specifies the desired string (sign bit padding)
		"""
		num = long(num)
		s = self.int2bitstring(num)
		if width:
			pad = '0'
			if num < 0:
				pad = '1'
				return (width - len(s)) * pad + s
		return s 

	
	def write_header(self):
		print >> self.f, "$date"
		print >> self.f, "    %s" % time.asctime()
		print >> self.f, "$end"
		print >> self.f, "$version"
		print >> self.f, "    PyDesk 0.0.1"
		print >> self.f, "$end"
		print >> self.f, "$timescale"
		print >> self.f, "    %s" % self.timescale
		print >> self.f, "$end"
		print >> self.f

	def write_sig_decl(self,comp):
		# Add signals from current component
		sigs = [it for it in self.sim.state_variables if it.parent==comp]
		print >> self.f, "$scope module "+comp.name+" $end"
		for s in sigs:
			s.vcd_id = self.namegen.next()
			print >> self.f, "$var wire "+str(s.bit_size)+" "+s.vcd_id+" "+s.name+" $end"
		# Add signals from child components
		if comp.has_children():
			for c in comp.get_children():
				self.write_sig_decl(c)
		# Close current scope
		print >> self.f, "$upscope $end"
	
	def write_sig_dump(self):
		# Initial values
		print >> self.f, "$dumpvars"
		for s in self.sim.state_variables:
			print >> self.f, "b%s %s" % (self.bin(s.first_value,s.bit_size), s.vcd_id)
		print >> self.f, "$end"
		# Dump value changes
		times = []
		for s in self.sim.state_variables:
			for t in s.history.keys():
				if not t in times:
					times.append(t)
		times.sort()
		for t in times:
			print >> self.f, "#%d" % (t)
			for s in self.sim.state_variables:
				if t in s.history.keys():
					print >> self.f, "b%s %s" % (self.bin(s.history[t],s.bit_size), s.vcd_id)
	
	def write_vcd(self):
		self.write_header()
		roots = filter(lambda x:self.sim.components[x]==None,self.sim.components.keys())
		for c in roots:
			self.write_sig_decl(c)
		print >> self.f, "$enddefinitions $end"
		self.write_sig_dump()
		self.f.close()
		
# Event - a message indicating that something has happened
class Event:
	def __init__(self,name="",sim=None):
		self.state=event_off
		self.async_callbacks = []
		self.sync_callbacks = []
		self.listeners = 0
		self.name = name
		self.sim = sim
		self.emit_time = -1
		self.sources = []
		self.source_states = { }
		self.counter = 0
		self.source_data = { }
		self.targets = []
		self.te_type = ""
	
	def consume(self):
		self.listeners = self.listeners-1 if self.listeners>0 else 0
		if self.listeners==0:
			self.state=event_off
	
	def add_listener(self):
		self.listeners+=1
	
	def emit(self):
		self.state=event_on
		self.run_async_callbacks()
		for target in self.targets:
			target.trigger(self)
		if self.sim!=None :
			self.sim.emitted_events.append(self)
			self.emit_time = self.sim.time
	
	def run_async_callbacks(self):
		for cb in self.async_callbacks:
			cb()
	
	def run_sync_callbacks(self):
		for cb in self.sync_callbacks:
			cb()
	
	def register_async_callback(self,cb):
		self.async_callbacks.append(cb)
	
	def register_sync_callback(self,cb):
		self.sync_callbacks.append(cb)
	
	def trigger(self,other):
		if other in self.source_states.keys():
			self.source_states[other]=event_on;

		if self.te_type=='>>':
			done=reduce(lambda x,y:x and y, self.source_states.values())
			if done:
				self.emit()
				for k in self.source_states.keys():
					self.source_states[k]=event_off

		elif self.te_type=="&":
			pass
		elif self.te_type=="|":
			done=reduce(lambda x,y:x or y, self.source_states.values())
			if done:
				self.emit()
				for k in self.source_states.keys():
					self.source_states[k]=event_off
		elif self.te_type=="<<":
			pass
		elif self.te_type=="*":
			if other in self.source_data.keys():
				if type(self.source_data[other]) is IntType:
					self.counter-=1
					if self.counter<=0:
						self.emit()
						self.counter=self.source_data[other]
				elif type(self.source_data[other]) is TupleType:
					pass
			

	def __rshift__(self, other):
		result=None
		if isinstance(other,Event):
			result=Event(self.name+'>>'+other.name,self.sim)
			self.targets.append(result)
			other.targets.append(result)
			result.source_states[self]=event_off
			result.source_states[other]=event_off
		elif type(other) is IntType:
			pass
		elif type(other) is TupleType:
			pass

		result.te_type=">>"
		return result
	
	def __or__(self,other):
		if isinstance(other,Event):
			result=Event(self.name+'|'+other.name,self.sim)
			self.targets.append(result)
			other.targets.append(result)
			result.source_states[self]=event_off
			result.source_states[other]=event_off
		elif type(other) is IntType:
			pass
		elif type(other) is TupleType:
			pass

		result.te_type="|"
		return result
	
	def __mul__(self,other):
		result = Event(self.name+'*'+str(other),self.sim)
		self.targets.append(result)
		result.source_data[self]=other
		result.counter=other
		result.te_type='*'
		return result
	def __rmul__(self,other):
		return self.__mul__(other)
		


# Component - a collection of threads,events and state variables
class Component:
	def __init__(self,name,parent=None):
		self.name=name
		self.sim = None
		self.parent = None
		if isinstance(parent, Simulator):
			self.sim=parent
		elif isinstance(parent, Component):
			self.sim=parent.sim
			self.parent=parent
		self.sim.register_component(self)
	
	def te(self,te):
		result_ev = Event(sim=self.sim)
		def te_thread(te_copy):
			do_emit = True
			prev_time = 0
			prev_type = ""
			while True:
				do_emit=True
				for e in te_copy:
					if(isinstance(e,(int,long,float))):
						yield wait_time,e
						prev_time = self.sim.time
						prev_type = "time"
					elif(isinstance(e,Event)):
						yield wait_event,e
						if prev_type=="time" and prev_time!=self.sim.time:
							prev_type = "event"
							do_emit = False
							break
						prev_type = "event"
					elif(type(e) is TupleType):
						if(len(e)==2):
							if(isinstance(e[0],(int,long,float)) and isinstance(e[1],Event)):
								for i in range(e[0]):
									yield wait_event,e[1]
									if i==0 and prev_type=="time" and prev_time!=self.sim.time:
										do_emit = False
										prev_type = "event"
										break
									prev_type = "event"
					else:pass # TODO : Crash with a severe error message
				if do_emit:
					result_ev.emit()
		self.start(te_thread(te))
		return result_ev
	
	def start(self,t):
		return self.sim.register_component_thread(self,t)
	
	def kill_thread(self,t):
		self.sim.kill_thread_by_handle(t)

	
	def on_event(self,ev,f):
		ev.add_callback(f)

	def get_children(self):
		children = []
		for c,p in self.sim.components.iteritems():
			if p==self:
				children.append(c)
		return children

	def has_children(self):
		return self in self.sim.components.values()
	
	def run(self):
		pass

# Not sure if it's useful
def Simulate(comp):
	comp.sim.simulate()

# State variables
class state_variable:
	def __init__(self,value=None,name="",parent=None):
		self.name=name
		self.sim=parent if isinstance(parent,Simulator) else parent.sim if isinstance(parent,Component) else None
		self.parent = parent
		self.first_value=0
		self.prev_value=0
		self.value=value
		self.others = []
		self.with_trace = True
		self.history = {}
		self.bit_size = 32
		self.rise = Event(sim=self.sim)
		self.fall = Event(sim=self.sim)
		self.change = Event(sim=self.sim)
		self.compare_func = None
		self.vcd_id='a'
		self.expr = lambda x:x[0]
		self.assign_var_list = []
		if self.sim!=None:
			self.sim.state_variables.append(self)
	
	def __le__(self,other):
		if(self.sim!=None):
			self.sim.schedule_assignment(self,other)
			for o in self.others:
				self.sim.schedule_assignment(o,other)
	
	def do_assign(self,other):
		self.value = other
			
	def do_update(self):
		# Update combinational assigns
		if self.assign_var_list!=[]:
			self.value = self.expr(self.assign_var_list)
		# Update signal history
		if self.with_trace and self.value!=self.prev_value:
			self.history[self.sim.time]=self.value
		# Emit events
		if(isinstance(self.value,(int,long,float))):
			if(self.value>self.prev_value): self.rise.emit()
			if(self.value<self.prev_value): self.fall.emit()
			if(self.value!=self.prev_value): self.change.emit()
		elif(self.compare_func!=None):
			if self.compare_func(self.value,self.prev_value)>0: self.rise.emit()
			if self.compare_func(self.value,self.prev_value)<0: self.fall.emit()
			if self.ompare_func(self.value,self.prev_value)!=0: self.change.emit()
		else:
			if(self.value!=self.prev_value): self.change.emit()
		#Update prev value
		self.prev_value=self.value
		# Update others
		for o in self.others:
			o.value = self.value
			o.do_update()
	
	def connect(self,other):
		self.others.append(other)

	def disconnect(self,other):
		self.others.remove(other)
	
	def assign_var(self,other):
		self.expr = lambda x: x[0]
		self.assign_var_list = [other]
	
	def assign_expr(self,expr,others):
		self.expr = expr
		self.assign_var_list = others


# Ports

## Method ports
class out_method_port:
	def __init__(self,name=""):
		self.other = None
		self.name = name
	
	def connect(self,o):
		self.other = o
	
	def disconnect(self):
		self.other=None
	
	def transfer_nb(self,*kargs,**kwargs):
		self.other.transfer(*kargs,**kwargs)
	
	def transfer_b(self,*kargs,**kwargs):
		return self.other.transfer(*kargs,**kwargs)

class in_method_port:
	def __init__(self,name,trans):
		self.transfer = trans
		self.name = name
		self.disconnected = True

class method_channel:
	pass

## Broadcast port
class out_bcast_port:
	def __init__(self,name):
		self.others  = []
		self.name = name
	
	def send(self,*kargs,**kwargs):
		for o in self.others:
			o.transfer(*kargs,**kwargs)

## Reactive ports
class in_reactive_port:
	def __init__(self,name):
		self.name = name
		self.value = None
	
	def nb_assign(self,other):
		pass
		


	def b_assign(self,other):
		pass

	
	def __le__(self,other):
		pass



class out_reactive_port:
	def __init__(self,name):
		self.name = name
		self.value = None

class reactive_channel:
	def __init__(self,name):
		self.name = name
		self.in_value = None
		self.out_value = None

## FIFO ports
class in_fifo_port(Component):
	def __init__(self,name,parent):
		pass

class out_fifo_port(Component):
	def __init__(self,name,parent):
		pass

class fifo_channel:
	pass

