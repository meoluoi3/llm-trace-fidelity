import gdb
import json
import os
import sys

trace_log = []
step_count = 0
last_seen_state = {}

WATCH_FILE = os.environ.get("WATCH_EXPRS_FILE", "watch_exprs.json")
TARGET_FUNC = os.environ.get("TARGET_FUNCTION", "_writeValueBegin")

with open(WATCH_FILE, "r", encoding="utf-8") as f:
    EXPRS_TO_WATCH = json.load(f)


def read_state():
    state = {}
    for expr in EXPRS_TO_WATCH:
        try:
            state[expr] = str(gdb.parse_and_eval(expr))
        except gdb.error:
            pass  
    return state


gdb.execute("set breakpoint pending on")
gdb.execute(f"break {TARGET_FUNC}")
gdb.execute("run")

while True:
    try:
        frame = gdb.selected_frame()
    except gdb.error:
        break

    name = frame.name()
    if name is None or TARGET_FUNC not in name:
        break

    line = frame.find_sal().line
    current_state = read_state()
    step_count += 1

    changed_vars = {}
    for k, v in current_state.items():
        if k not in last_seen_state:
            changed_vars[k] = f"{v} (new)"
        elif last_seen_state[k] != v:
            changed_vars[k] = f"{v} (changed)"

    last_seen_state.update(current_state)

    if changed_vars:
        state_str = ", ".join([f"{k} = {v}" for k, v in changed_vars.items()])
        log_entry = f"[Step {step_count}] Line {line}. Changes: {{ {state_str} }}"
    else:
        log_entry = f"[Step {step_count}] Line {line}. (No changes)"

    trace_log.append(log_entry)

    try:
        gdb.execute("next", to_string=True)
    except Exception as e:
        print(e)
        raise

with open("visited_trace.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(trace_log))

gdb.execute("quit")