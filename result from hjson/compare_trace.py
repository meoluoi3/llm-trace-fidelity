import json
import sys

def load(path):
    with open(path) as f:
        return json.load(f)

def compare(gt, pred):
    n = min(len(gt), len(pred))
    total_vars = 0
    mismatches = []
    for i in range(n):
        gt_step, pred_step = gt[i], pred[i]
        if gt_step["line"] != pred_step.get("line"):
            mismatches.append({
                "step": i, "type": "WRONG_LINE",
                "gt_line": gt_step["line"], "pred_line": pred_step.get("line")
            })
            continue
        for var, gt_val in gt_step["vars"].items():
            total_vars += 1
            pred_val = pred_step.get("vars", {}).get(var)
            if pred_val is None:
                mismatches.append({"step": i, "line": gt_step["line"], "type": "MISSING_VAR", "var": var})
            elif str(pred_val).strip() != str(gt_val).strip():
                mismatches.append({
                    "step": i, "line": gt_step["line"], "type": "WRONG_VALUE",
                    "var": var, "gt": gt_val, "pred": pred_val
                })

    n_wrong_line = sum(1 for m in mismatches if m["type"] == "WRONG_LINE")
    n_wrong_val = sum(1 for m in mismatches if m["type"] == "WRONG_VALUE")

    print(f"Steps compared: {n}")
    print(f"Total (step, var) checks: {total_vars}")
    print(f"Wrong branch/line order: {n_wrong_line}")
    print(f"Wrong variable value: {n_wrong_val} ({n_wrong_val/max(total_vars,1)*100:.1f}%)")
    print(f"Trace fidelity (var-level accuracy): {(1 - len(mismatches)/max(total_vars,1))*100:.1f}%")
    print()
    print("First mismatches found (max 10):")
    for m in mismatches[:10]:
        print(" ", m)
    return mismatches

if __name__ == "__main__":
    gt = load(sys.argv[1])
    pred = load(sys.argv[2])
    compare(gt, pred)

# ---- Prompt template to get llm_trace.json from the LLM ----
#
# IMPORTANT (lesson learned from the classify() run): paste the WHOLE file
# the ground-truth trace was taken from, exactly as-is, not just the
# function body. If you paste only the function, the LLM counts "line 1"
# as the function signature, while gdb_tracer.py reports real file line
# numbers (which include includes/comments above the function) -- the two
# will disagree on line numbers even when the reasoning is otherwise
# correct, and every step gets misclassified as WRONG_LINE.
#
# For _writeValueBegin specifically, also paste the Encoder struct and
# EncodeParent/EncodeState definitions it depends on (from hjson.h /
# hjson_encode.cpp), so the LLM has the real field names (e->indent,
# e->opt.comments) instead of guessing.
PROMPT_TEMPLATE = '''
Here is the exact source file src/hjson_encode.cpp (line numbers below
match this file exactly -- do not renumber):
<paste the WHOLE file content here, or at minimum the full function
_writeValueBegin plus the struct definitions it depends on (Encoder,
EncodeParent, EncodeState), keeping their real line numbers>

Specific input: a Hjson::Value of type Vector containing [1, 2, 3],
default DecoderOptions (comments=true).

Simulate the execution of _writeValueBegin LINE BY LINE for just the
FIRST call (the outer vector, before it returns to process element 0).
Do not skip lines, do not summarize. After EACH line executed, print
exactly this JSON format, using the REAL line numbers from the file
above:
{"line": <line number>, "vars": {"value.type()": "...", "e->indent": "...", "e->opt.comments": "..."}}

Only list variables/fields that already exist at that point (skip
anything not yet bound/assigned). Return ONE JSON array containing all
steps, with no extra explanation, no markdown code fence.
'''