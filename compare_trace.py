import json
import sys

def load(path):
    with open(path) as f:
        return json.load(f)

def compare(truth,llm):
    n = min(len(truth), len(llm))
    mismatches = []

    for i in range(n):
        tstep = truth[i]
        llmstep = llm[i]

        # Check if the lines match
        if tstep["line"] != llmstep["line"]:
            mismatches.append({
                "step": i,
                "type": "line",
                "truth_line": tstep["line"],
                "llm_line": llmstep["line"]
            })
            continue

        for var_name, truth_val in tstep["vars"].items():
            llm_val = llmstep.get("vars", {}).get(var_name)

            if llm_val is None:
                mismatches.append({
                    "step": i, 
                    "line": tstep["line"], 
                    "type": "MISSING_VAR", 
                    "var": var_name
                })
            elif str(truth_val).strip() != str(llm_val).strip():
                mismatches.append({
                    "step": i, 
                    "line": tstep["line"], 
                    "type": "WRONG_VALUE",
                    "var": var_name, 
                    "truth": truth_val, 
                    "llm": llm_val
                })

    print(f"No. of lines compared: {n}")
    print(f"No. of mismatches: {len(mismatches)}")
    for m in mismatches[:10]: # print first 10 mismatches
        print(" -", m)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_trace.py <truth.json> <llm.json>")
        sys.exit(1)

    truth_data = load(sys.argv[1])
    llm_data = load(sys.argv[2])
    compare(truth_data, llm_data)