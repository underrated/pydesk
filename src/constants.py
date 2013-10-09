# Simulator states
delta_limit_reached = -3
simulation_deadlock = -2
end_of_time = -1
end_of_simulation = 0
continue_simulation = 1

# Thread states
thread_running = "thread_running"
thread_waiting_time = "thread_waiting_time"
thread_waiting_event = "thread_waiting_event"
thread_waiting_thread = "thread_waiting_thread"
thread_finished = "thread_finished"
thread_join_all = "thread_join_all"
thread_join_first = "thread_join_first"
thread_join_any = "thread_join_any"

# Simulator commands
## Wait statements(context switches)
wait_time = "wait_time"
wait_event = "wait_event"
wait_thread = "wait_thread"
## Query commands
## (they don't allow other threads to continue)
## (they are only uses as simulator-thread communication channels)
sim_cmd = "sim_cmd"
get_thread_self = "get_thread_self"
get_children_threads = "get_children_threads"
start_thread = "start_thread"
join_all = "join_all"
join_first = "join_first"
join_any = "join_any"

stop_simulation = "stop_simulation"

# Event states
event_on=1
event_off=0

# Timescales
sim_ns = 1e-9
sim_us = 1e-6
sim_ms = 1e-3
sim_seconds  = 1
sim_minutes = 60
sim_hours = 3600 

# Verbosity levels
NONE = 0
LOW = 1
MEDIUM = 2
HIGH = 3
FULL = 4
