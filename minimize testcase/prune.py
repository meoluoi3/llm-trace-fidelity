import subprocess
import glob
import json
import re
import os
import sys

HJSON_SRC_DIR = "../hjson-cpp/src"
HJSON_INCLUDE_DIR = "../hjson-cpp/include/hjson"

def get_cpp_files_to_compile(driver_path):
    with open(driver_path, 'r', encoding='utf-8') as f:
        driver_code = f.read()
        
    all_cpp_files = glob.glob(f"{HJSON_SRC_DIR}/*.cpp")
    cpp_files = []
    for f in all_cpp_files:
        file_name = os.path.basename(f)
        if file_name in driver_code:
            continue
        cpp_files.append(f)
    return cpp_files

def compile_driver(driver_path):
    cpp_files = get_cpp_files_to_compile(driver_path)
    compile_cmd = ["g++", "-g", "-O0", driver_path] + cpp_files + [
        "-I", HJSON_INCLUDE_DIR, "-o", "target.exe"
    ]
    return subprocess.run(compile_cmd, capture_output=True, text=True)

def get_coverage(driver_path) -> float:
    gcov_out = subprocess.run(["gcov", driver_path], capture_output=True, text=True).stdout
    
    target_cov = 0.0
    lines = gcov_out.split('\n')
    for i, line in enumerate(lines):
        if "File '" in line and "hjson_" in line and ".cpp" in line:
            if i + 1 < len(lines) and "Lines executed:" in lines[i+1]:
                m = re.search(r"Lines executed:([\d.]+)%", lines[i+1])
                if m: 
                    target_cov = float(m.group(1))
                    return target_cov 

    line_matches = re.findall(r"Lines executed:([\d.]+)%", gcov_out)
    if line_matches: 
        target_cov = float(line_matches[-1])
        
    return target_cov

def verify_driver_ok(driver_path, baseline_coverage) -> bool:
    cpp_files = get_cpp_files_to_compile(driver_path)
    
    compile_cmd = ["g++", "-g", "-O0", "--coverage", driver_path] + cpp_files + ["-I", HJSON_INCLUDE_DIR, "-o", "target.exe"]
    if subprocess.run(compile_cmd, capture_output=True).returncode != 0:
        return False
        
    subprocess.run(["target.exe"], capture_output=True)
    
    current_coverage = get_coverage(driver_path)
    
    return current_coverage >= baseline_coverage

def is_removable_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("//") or stripped.startswith("return") or stripped.startswith("std::cout"):
        return False
    return bool(re.match(r"^[\w\.\->\[\]]+\s*=.*;$", stripped)) or \
           bool(re.match(r"^[\w_]+\(.*\);$", stripped))

def main():
    if len(sys.argv) < 4:
        print("Usage: python prune.py <driver.cpp> <target_function> <target_line> [dfg_slice_file.json]")
        return

    driver_path = sys.argv[1]
    target_function = sys.argv[2]
    target_line = int(sys.argv[3])
    slice_file = sys.argv[4] if len(sys.argv) > 4 else f"dfg_slice_line{target_line}.json"

    with open(driver_path, "r", encoding="utf-8") as f:
        original_lines = f.readlines()

    slice_hint = set()
    if os.path.exists(slice_file):
        with open(slice_file, "r", encoding="utf-8") as f:
            slice_hint = set(json.load(f).get("relevant_vars", []))
        print(f"Loaded static slice hint: {slice_hint}")
    else:
        print(f"WARNING: {slice_file} not found, proceeding sequentially.")

    current_lines = list(original_lines)
    removed_log = []
    kept_despite_not_in_slice = []

    print("Measuring Baseline Coverage...")
    compile_res = compile_driver(driver_path)
    if compile_res.returncode != 0:
        print("ERROR: Cannot compile the original driver file!")
        print("GCC Error Details:\n", compile_res.stderr)
        sys.exit(1)

    cpp_files = get_cpp_files_to_compile(driver_path)
    subprocess.run(["g++", "-g", "-O0", "--coverage", driver_path] + cpp_files + ["-I", HJSON_INCLUDE_DIR, "-o", "target.exe"])

    subprocess.run(["target.exe"], capture_output=True)
    
    baseline_coverage = get_coverage(driver_path)
    print(f"Baseline Coverage: {baseline_coverage}%")

    candidate_indices = [i for i, line in enumerate(current_lines) if is_removable_line(line)]
    print(f"Found {len(candidate_indices)} candidate lines for removal.")

    def priority(idx):
        line = current_lines[idx]
        normalized = re.sub(r"\s+", "", line.split("=")[0])
        in_slice = any(v in normalized for v in slice_hint)
        return 0 if not in_slice else 1

    candidate_indices.sort(key=priority)

    for idx in candidate_indices:
        line_text = current_lines[idx].strip()
        print(f"\nAttempting to remove line {idx+1}: {line_text}")

        backup = current_lines[idx]
        current_lines[idx] = ""

        with open(driver_path, "w", encoding="utf-8") as f:
            f.writelines(current_lines)

        still_ok = verify_driver_ok(driver_path, baseline_coverage)

        if still_ok:
            print("  -> REMOVED")
            removed_log.append({"line_number": idx + 1, "content": line_text})
        else:
            print("  -> KEPT")
            current_lines[idx] = backup
            normalized = re.sub(r"\s+", "", line_text.split("=")[0])
            was_predicted_removable = not any(v in normalized for v in slice_hint)
            if was_predicted_removable:
                kept_despite_not_in_slice.append({
                    "line_number": idx + 1, "content": line_text,
                    "note": "Static slice predicted redundant but could NOT be removed"
                })

    with open(driver_path, "w", encoding="utf-8") as f:
        f.writelines(current_lines)

    result = {
        "driver_file": driver_path,
        "original_line_count": len(original_lines),
        "pruned_line_count": len(current_lines),
        "removed_lines": removed_log,
        "kept_despite_not_in_slice": kept_despite_not_in_slice,
    }
    with open("pruning_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n=== RESULTS ===")
    print(f"Successfully removed {len(removed_log)}/{len(candidate_indices)} lines.")
    print(f"Static slice incorrect predictions: {len(kept_despite_not_in_slice)} lines.")
    print(f"Details saved to pruning_report.json")

if __name__ == "__main__":
    main()