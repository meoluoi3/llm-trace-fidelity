import gdb
import json
# gdb -q -batch -x gdb_tracer.py --args ./target vector
trace = []

# Unlike classify() where state lived in 5 flat local variables, the state
# _writeValueBegin cares about lives in two places:
#   - fields of the Encoder struct, reached through a pointer "e" (e->indent,
#     e->opt.comments) -- same "->" pattern as p->ch in the earlier example.
#   - the Value being written, reached through the local reference "value"
#     (value.type() calls a real method, not a plain field -- gdb can still
#     evaluate it as long as the binary is built with -O0 so the method call
#     isn't inlined away).
EXPRS_TO_WATCH = ["value.type()", "e->indent", "e->opt.comments"]

def read_state():
    state = {}
    for expr in EXPRS_TO_WATCH:
        try:
            state[expr] = str(gdb.parse_and_eval(expr))
        except gdb.error:
            pass  # not in scope yet (e.g. before "value" is bound on line 1)
    return state

# _writeValueBegin is a "static" (internal-linkage) function, same as
# classify() was in the earlier example -- breaking on the bare name works
# as long as it isn't ambiguous with another function of the same name
# elsewhere in the binary.
gdb.execute("break _writeValueBegin")
gdb.execute("run")

while True:
    frame = gdb.selected_frame()
    if "_writeValueBegin" not in frame.name():
        break
    line = frame.find_sal().line
    state = read_state()
    trace.append({"line": line, "vars": state})
    try:
        # "next", not "step": _writeValueBegin calls into Value:: methods
        # (type(), to_string(), get_comment_key()...) and _quote(). Stepping
        # into those would leave this function's frame and break the loop
        # early, same failure mode as with std::vector's constructor before.
        gdb.execute("next", to_string=True)
    except gdb.error:
        break

with open("truth_trace.json", "w") as f:
    json.dump(trace, f, indent=2)

print(f"Wrote {len(trace)} steps to truth_trace.json")
gdb.execute("continue", to_string=True)