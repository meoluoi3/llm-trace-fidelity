import gdb
import json
import os
import sys

trace_log = []
step_count = 0
last_seen_state = {}
source_cache = {}

WATCH_FILE = os.environ.get("WATCH_EXPRS_FILE", "watch_exprs.json")
TARGET_FUNC = os.environ.get("TARGET_FUNCTION", "_writeValueBegin")

with open(WATCH_FILE, "r", encoding="utf-8") as f:
    EXPRS_TO_WATCH = json.load(f)


def read_state():
    state = {}
    for expr in EXPRS_TO_WATCH:
        try:
            val = str(gdb.parse_and_eval(expr))
            if "{" in val and "}" in val and "0x" in val and "<" in val:
                continue  # Skip printing raw pointer addresses for structs/classes
            if "non-dereferenceable" in val:
                continue
            state[expr] = val
        except gdb.error:
            pass  
    return state

def get_source_line_text(filename, line_number):
    """return the text of a specific line from a source file, using a cache to avoid repeated file reads."""
    if not filename or not os.path.exists(filename):
        return ""
    
    if filename not in source_cache:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                source_cache[filename] = f.readlines()
        except Exception:
            return ""
            
    lines = source_cache[filename]
    if 0 < line_number <= len(lines):
        return lines[line_number - 1].strip()
    return ""

gdb.execute("set breakpoint pending on")
# gdb.execute(f"break {TARGET_FUNC}")
gdb.execute(f"break hjson_encode.cpp:{TARGET_FUNC}")
gdb.execute("run")

while True:
    try:
        frame = gdb.selected_frame()
    except gdb.error:
        break

    name = frame.name()
    if name is None or TARGET_FUNC not in name:
        break

    sal = frame.find_sal()
    line = sal.line
    filename = sal.symtab.fullname() if sal.symtab else None
    source_text = get_source_line_text(filename, line)
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
        state_str = "\n".join([f"{k} = {v}" for k, v in changed_vars.items()])
        log_entry = f"[Step {step_count}] Line {line}. {source_text} : Changes: {{ {state_str} }}"
    else:
        log_entry = f"[Step {step_count}] Line {line}. {source_text} : (No changes)"

    trace_log.append(log_entry)

    try:
        gdb.execute("next", to_string=True)
    except Exception as e:
        print(e)
        raise

with open("visited_trace.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(trace_log))

gdb.execute("quit")