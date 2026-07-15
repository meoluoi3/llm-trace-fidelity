# step2_compile.py
import subprocess
import glob
import json
import re
import os
from extract_AST import get_context

with open("run_config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

HJSON_SRC_DIR = "../hjson-cpp/src"
HJSON_INCLUDE_DIR = "../hjson-cpp/include/hjson"
EXCLUDED_SOURCE_FILE = "hjson_encode.cpp"
DRIVER_PATH = "test_driver.cpp"
LOG_PATH = "run_log.json"


def load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(log):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def extract_code_block(text: str) -> str:
    match = re.search(r"```(?:cpp|c\+\+)?\s*\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def compile_driver(driver_path):
    all_cpp_files = glob.glob(f"{HJSON_SRC_DIR}/*.cpp")
    cpp_files = [f for f in all_cpp_files if EXCLUDED_SOURCE_FILE not in f.replace('\\', '/')]
    compile_cmd = ["g++", "-g", "-O0", driver_path] + cpp_files + [
        "-I", HJSON_INCLUDE_DIR, "-o", "target.exe"
    ]
    return subprocess.run(compile_cmd, capture_output=True, text=True)


def main():
    if not os.path.exists("response.txt"):
        print("Chưa có response.txt — paste code LLM vào file này trước.")
        return

    with open("response.txt", "r", encoding="utf-8") as f:
        raw_response = f.read()

    code = extract_code_block(raw_response)

    with open(DRIVER_PATH, "w", encoding="utf-8") as f:
        f.write(code)

    result = compile_driver(DRIVER_PATH)
    success = result.returncode == 0

    log = load_log()
    step_num = len(log) + 1
    log.append({
        "step": step_num,
        "phase": "compile_check",
        "code": code,
        "success": success,
        "error": None if success else result.stderr,
    })
    save_log(log)

    print(f"[Step {step_num}] compile success = {success}")

    if success:
        print("PASSED. Chạy step3_trace.py tiếp theo.")
        return

    print("FAILED. Đang tạo fix_prompt.txt...")
    context = get_context(CONFIG["source_file"], CONFIG["target_function"])
    template = load_prompt_template("prompt_compilation_fix.txt")
    fix_prompt = template.format(
        previous_code=code,
        compiler_errors=result.stderr,
        context=context,
    )
    with open("fix_prompt.txt", "w", encoding="utf-8") as f:
        f.write(fix_prompt)

    print("Saved fix_prompt.txt — copy vào LLM, paste kết quả vào response.txt, rồi chạy lại step2_compile.py")


if __name__ == "__main__":
    main()