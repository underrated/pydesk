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
fork_join = "fork_join"
fork_join_none = "fork_join_none"
fork_join_any = "fork_join_any"
all_of = "all_of"
first_of = "first_of"

# Event states
event_on=1
event_off=0
