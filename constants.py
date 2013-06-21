# Simulator states
delta_limit_reached = -3
simulation_deadlock = -2
end_of_time = -1
end_of_simulation = 0
continue_simulation = 1

# Thread states
thread_running = 0
thread_waiting_time = 1
thread_waiting_event = 2
thread_waiting_thread = 3
thread_finished = 4

# Simulator commands
## Wait statements(context switches)
wait_time = 0
wait_event = 1
wait_thread = 2
## Query commands
## (they don't allow other threads to continue)
## (they are only uses as simulator-thread communication channels)
sim_cmd = 3
get_thread_self = 4
get_children_threads = 5
start_thread = 6
fork_join = 7
fork_join_none = 8
fork_join_any = 9
all_of = 10
first_of = 11

# Event states
event_on=1
event_off=0
