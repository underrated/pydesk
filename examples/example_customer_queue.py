import random
from pydesk import *

class Customer(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.arrival_time = random.randint(1,10)
		self.served = Event("served",self.sim)
		self.done = False
	
	def main_thread(self):
		# import pdb; pdb.set_trace() # TODO : remove
		sim.message("Customer "+self.name," is going to the store...",NONE)
		yield wait_time,self.arrival_time
		self.parent.register_customer(self)
		sim.message("Customer "+self.name," arrived at the store and is waiting in line...")
		yield wait_event,self.served
		self.done = True
		sim.message("Customer "+self.name," has been served and left the store...")
	
	def run(self):
		self.start(self.main_thread())

class Store(Component):

	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.customers = []
		self.mth = None
	
	def register_customer(self,customer):
		self.customers.append(customer)
	
	def serve_customer(self):
		c = self.customers.pop(0)
		sim.message("Store.serve_customer","Serving customer {0}".format(c.name),NONE)
		c.served.emit() # RULE : emit event before context switch
		yield wait_time,1
		sim.message("Store.serve_customer","Served customer {0}".format(c.name),NONE)
	
	def main_thread(self):
		while True:
			if len(self.customers)!=0:
				self.sim.message("Store.main_thread","We have customers...",NONE)
				yield wait_thread,self.serve_customer()
				self.sim.message("Store.main_thread","Served a customer...",NONE)
			else:
				self.sim.message("Store.main_thread","No customers in line yet, waiting...",NONE)
				yield wait_time,1
				self.sim.message("Store.main_thread","End of while loop, going for another iteration...",NONE)
	
	def run(self):
		self.mth = self.start(self.main_thread())
	

class Top(Component):
	def __init__(self,name,parent):
		Component.__init__(self,name,parent)
		self.my_store = Store("The Store",self)
		self.my_customers = []
		self.John   = Customer("John",   self.my_store); self.my_customers.append(self.John)
		self.Eric   = Customer("Eric",   self.my_store); self.my_customers.append(self.Eric)
		self.Stan   = Customer("Stan",   self.my_store); self.my_customers.append(self.Stan)
		self.Janet  = Customer("Janet",  self.my_store); self.my_customers.append(self.Janet)
		self.Claire = Customer("Claire", self.my_store); self.my_customers.append(self.Claire)

	def main_thread(self):
		while True:
			states = map(lambda c:c.done, self.my_customers)
			if False in states:
				sim.message("Top","We have unserved customers, waiting...\n {0}".format(str(states)))
				yield wait_time,1
			else:
				sim.message("Top","All customers have been served, stopping simulation")
				self.kill_thread(self.my_store.mth)
				break
	def run(self):
		self.start(self.main_thread())

sim = Simulator()
sim.verbose = 0
my_top = Top("my_top",sim)
sim.simulate_comp()
	
