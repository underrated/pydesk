===================
Py-DESK v0.0.1beta
===================

Py-DESK is a Discrete Event Simulation library written in python.

It makes use of python's generators to implement a discrete event simulation 
kernel around which you can build simulation software.

DESK is an abbreviation for Discrete Event Simulation Kernel.

Typical usage often looks like this::

    from pydesk import *

    # Implement one or more components
    class my_comp(Component):
        # Simulation logic
        # ...

    # Create a simulator
    sim = Simulator() 
    
    # Create components and register them with the simulator
    my_comp_inst = my_comp("comp_name",sim) 

    # Run the simulation
    sim.simulate() 

Threads
========

Threads are methods that can run in parallel. They are implemented using python generators so
when implementing a thread you must use at least once the yield statement together with a valid
simulator command. Every time the yield command is used, the control is passed to the simulator
which updates the simulation state and allows other threads to advance with their execution.

A thread implementation usually looks like this::
    
    def my_thread():
        # do something here...
	yield wait_time,10
        # do something else here...
	yield wait_event,some_event
        # do some more stuff here...
        # etc.

Please notice the usage of the yield statement. You must always specify a valid simulator command
followed by arguments for that command.

Currently Py-DESK supports the following simulator commands:

* wait_time, <some_time> - tell the simulator to consume simulation time
* wait_event, <some_event> - tell the simulator to wait for an event to be emitted
* wait_thread, <some_thread> - tell the simulator to wait for a thread to finish execution

In order to run a thread you must register it with the simulator and start the simulation
This is done like this::

sim=Simulator()
sim.register_thread( my_thread() )
sim.simulate()

Simulation time
================

In order to consume simulation time the wait_time command must be used like this::

    def my_thread():
        print "Step 1"
	yield wait_time,10
	print "Step 2"

Py-DESK does not currently support units of measurement of time so you can interpret the amount
of consumed simulation time any way you want. I might add in future releases support for units of measurement.

Simulation time is not the same thing as the wall-clock time. The wall-clock time is the human perception of
the passage of time. Simulation time is just a simulation state variable managed by the simulator. One second
of simulation can last longer or shorter than a wall-clock second depending on how much it takes the simulator
to advance the simulation time by one second.

Events
========

An event is a message indicating that something has happened. Events can be emitted and waited on like this::

    def emitting_thread():
    	some_event.emit()
	yield wait_time, 0
    
    def waiting_thread():
        yield wait_event, some_event
        # Resume execution

Please notice that after we emit the event in the emitting thread we consume 0 simulation time. The emit statement
does not consume simulation time and does not pass control to the simulator. It only modifies the state of the event.
In order for other threads to be notified about this state change control must be passed to the simulator by the emitting 
thread through a yield statement. Consuming 0 simulation time is the most common way but not the only way. Caution must be
taken when considering other solutions as unexpected effects might occur. 

Components
===========

Threads and simulation state variables can be grouped together into components. 
Components can be implemented like this::

    class my_component(Component):
        def __init__(self,name,parent):
	    Component.__init__(self,name,parent)
            # add other state variables
            self.my_state_var = 0
            # or other sub-components 
	    self.other_comp_inst = other_comp("other_comp",self)
	
	def my_thread(self):
	    print "Hello at time 0"
	    yield wait_time, 1
	    print "Hello at time 1"

	def run(self):
	    self.start(my_thread)

In the constructor of a component you MUST call the constructor of the Component class.
When instantiating a sub-component make sure to set its parent as the current class.
In order to simulate a component you must register it with the simulator and start
the simulation like this::

    sim = Simulator()
    comp = my_component("comp",sim)
    sim.simulate_comp() 

Please notice that calling the constructor of the my_component class automatically registers
the class instance with the simulator. The same happens with sub-components.

The initialization of a component is done in the run method. Here you usually start the main threads.
Run methods are run recursivelly over the component hierarchy from top to bottom.

Data Flow
=========



Examples
========

To see examples of how the features of the simulator are used you can look through the unit tests
and through the customer queue example.

Installation
=============

Currently Py-DESK is not an installable python package. You must copy the files pydesk.py
and constants.py to your local work folder or add the PyDesk folder to PYTHONPATH.
Only then can you import what you need from the pydesk module.

I am still in the phase of learning python and it's still not clear to me how to create
an installable python package. Some help would be appreciated.

Bugs
====

Since this is the very release first don't expect it to work perfectly.

Contact
=======

For suggestions and/or other type of feedback you can contact me at:

yourstruly@underrated.org



