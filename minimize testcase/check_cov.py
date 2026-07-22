# check_cov.py
import subprocess
import glob
import os
import sys

if len(sys.argv) < 2:
    print("Error: Please provide the C++ driver filename.")
    print("Usage: python check_cov.py <driver_filename.cpp>")
    sys.exit(1)

driver_path = sys.argv[1]

if not os.path.exists(driver_path):
    print(f"Error: File '{driver_path}' not found.")
    sys.exit(1)

driver_name = os.path.splitext(os.path.basename(driver_path))[0]
OUTPUT_DIR = os.path.join("coverage_data", driver_name)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Đã đổi đường dẫn sang tinyxml2
TARGET_SRC_DIR = "../tinyxml2"
TARGET_INCLUDE_DIR = "../tinyxml2"

print("0. Cleaning up old build artifacts in current directory...")
for f in glob.glob("*.gcda") + glob.glob("*.gcno") + glob.glob("*.gcov") + glob.glob("target.exe"):
    try:
        os.remove(f)
    except OSError:
        pass

with open(driver_path, 'r', encoding='utf-8') as f:
    driver_code = f.read()

# Exclude any included cpp and the built-in xmltest.cpp
cpp_files = []
for f in glob.glob(f"{TARGET_SRC_DIR}/*.cpp"):
    filename = os.path.basename(f)
    if filename not in driver_code and filename != "xmltest.cpp":
        cpp_files.append(f)

print(f"1. Compiling {driver_path} with --coverage flag...")
cmd = ["g++", "-g", "-O0", "--coverage", driver_path] + cpp_files + [
    "-I", TARGET_INCLUDE_DIR, "-o", "target.exe"
]
compile_res = subprocess.run(cmd, capture_output=True, text=True)
if compile_res.returncode != 0:
    print("COMPILATION ERROR:\n", compile_res.stderr)
    sys.exit(1)

print("2. Running target.exe...")
run_res = subprocess.run(["target.exe"], capture_output=True, text=True)
if run_res.returncode != 0:
    print(f"WARNING: target.exe exited with code {run_res.returncode}")
    print(run_res.stdout)
    print(run_res.stderr)
else:
    print(run_res.stdout)

gcda_files = glob.glob("*.gcda")
if not gcda_files:
    print("Error: No .gcda files found. Execution may have crashed before coverage was written.")
    sys.exit(1)

print(f"3. Generating coverage reports (HTML + JSON + CSV) into '{OUTPUT_DIR}/'...")

html_path = os.path.join(OUTPUT_DIR, "coverage.html")
json_path = os.path.join(OUTPUT_DIR, "coverage.json")
csv_path = os.path.join(OUTPUT_DIR, "coverage.csv")
summary_path = os.path.join(OUTPUT_DIR, "summary.txt")

# Đã đổi bộ lọc regex sang tinyxml2
gcovr_base = [
    "gcovr",
    "--root", "..",
    "--filter", r".*tinyxml2.*\.cpp",
    "--branches",
]

subprocess.run(gcovr_base + ["--html", "--html-details", "-o", html_path], capture_output=True, text=True)
subprocess.run(gcovr_base + ["--json", "-o", json_path], capture_output=True, text=True)
subprocess.run(gcovr_base + ["--csv", "-o", csv_path], capture_output=True, text=True)

summary_res = subprocess.run(gcovr_base, capture_output=True, text=True)
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary_res.stdout)

print("\n=== COVERAGE SUMMARY ===")
print(summary_res.stdout)

print(f"\nReports saved to: {OUTPUT_DIR}/")
print(f"  - {html_path}  (open in browser, line + branch highlighted)")
print(f"  - {json_path}  (machine-readable, per-file/per-line detail)")
print(f"  - {csv_path}   (spreadsheet-friendly summary)")
print(f"  - {summary_path}")

print("\n4. Cleaning workspace (moving raw gcov artifacts out of the way)...")
for f in glob.glob("*.gcda") + glob.glob("*.gcno") + ["target.exe"]:
    if os.path.exists(f):
        try:
            os.remove(f)
        except OSError:
            pass