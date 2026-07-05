import gdb
import json
# gdb -q -batch -x gdb_tracer.py --args ./target '{"a":"{}"}'
trace = []

# Variables to trace
VARS_TO_TRACE = ["depth", "in_quote", "x", "i", "c"]

def read_locals(frame):
    state = {}
    for name in VARS_TO_TRACE:
        try:
            val = frame.read_var(name)
            state[name] = str(val)
        except gdb.error:
            pass
    return state

# putting breakpoint on the classify func
gdb.execute("break classify")
gdb.execute("run")

while True:
    frame = gdb.selected_frame()
    # Stop the loop when exiting the classify function
    if frame.name() != "classify":
        break  

    line = frame.find_sal().line
    state = read_locals(frame)   
    trace.append({"line": line, "vars": state})

    try:
        gdb.execute("step", to_string=True) # Step to the next line 
    except gdb.error:
        break

with open("truth_trace.json", "w") as f:
    json.dump(trace, f, indent=2)

print(f"Wrote {len(trace)} steps to truth_trace.json")
gdb.execute("continue", to_string=True)