import subprocess
import glob
import os
import sys
import re

HJSON_SRC_DIR = "../hjson-cpp/src"
HJSON_INCLUDE_DIR = "../hjson-cpp/include/hjson"
EXCLUDED_SOURCE_FILE = "hjson_encode.cpp"

def clean_old_coverage_files():
    for pattern in ["*.gcda", "*.gcno", "*.gcov", "*.exe"]:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
            except OSError:
                pass

def compile_all_drivers_with_coverage(driver_files):
    all_cpp_files = glob.glob(f"{HJSON_SRC_DIR}/*.cpp")
    cpp_files = [f for f in all_cpp_files if EXCLUDED_SOURCE_FILE not in f.replace('\\', '/')]

    for i, driver in enumerate(driver_files):
        compile_cmd = [
            "g++", "-g", "-O0", "--coverage",
            driver
        ] + cpp_files + [
            "-I", HJSON_INCLUDE_DIR,
            "-o", f"target_{i}.exe"
        ]
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"COMPILE FAILED for {driver}:\n{result.stderr}")
            continue
        
        subprocess.run([f"./target_{i}.exe"], capture_output=True, text=True)
        print(f"Ran {driver} -> target_{i}.exe")

def run_gcov(driver_files):
    total_output = ""
    for driver in driver_files:
        result = subprocess.run(
            ["gcov", driver],
            capture_output=True, text=True, cwd="."
        )
        print(f"\n--- gcov output for {driver} ---")
        print(result.stdout)
        total_output += result.stdout + "\n"
    return total_output

def parse_gcov_summary(gcov_output: str):
    line_matches = re.findall(r"Lines executed:([\d.]+)% of (\d+)", gcov_output)
    branch_matches = re.findall(r"Branches executed:([\d.]+)% of (\d+)", gcov_output)

    result = {}
    if line_matches:
        result["line_coverage_pct"] = float(line_matches[-1][0])
        result["total_lines"] = int(line_matches[-1][1])
    if branch_matches:
        result["branch_coverage_pct"] = float(branch_matches[-1][0])
        result["total_branches"] = int(branch_matches[-1][1])
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python coverage_checker_gcov.py <driver1.cpp> [driver2.cpp ...]")
        return

    driver_files = sys.argv[1:]

    clean_old_coverage_files()
    compile_all_drivers_with_coverage(driver_files)

    gcov_output = run_gcov(driver_files)
    summary = parse_gcov_summary(gcov_output)

    print("\n=== SUMMARY (from gcov) ===")
    print(summary)

if __name__ == "__main__":
    main()