# step3_trace.py
import subprocess
import json
import re
import os

with open("run_config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

TARGET_LINE = CONFIG.get("target_line", 375)
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


def run_gdb_trace():
    if os.path.exists("visited_trace.txt"):
        os.remove("visited_trace.txt")

    env = os.environ.copy()
    env["TARGET_FUNCTION"] = CONFIG["target_function"]
    env["WATCH_EXPRS_FILE"] = "watch_exprs.json"

    run_cmd = ["gdb", "-q", "--batch", "-x", "gdb_tracer.py", "--args", "./target.exe"]
    result = subprocess.run(run_cmd, capture_output=True, text=True, env=env)

    if not os.path.exists("visited_trace.txt"):
        raise RuntimeError(
            f"visited_trace.txt not found. GDB tracer có thể đã crash.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    with open("visited_trace.txt", "r", encoding="utf-8") as f:
        return f.read()


def target_branch_reached(trace_text: str) -> bool:
    pattern = rf"\[Step \d+\] Line {TARGET_LINE}\."
    return re.search(pattern, trace_text) is not None


def main():
    if not os.path.exists(DRIVER_PATH) or not os.path.exists("target.exe"):
        print("Chưa có driver compiled. Chạy step2_compile.py tới khi PASSED trước.")
        return

    trace = run_gdb_trace()
    reached = target_branch_reached(trace)

    log = load_log()
    step_num = len(log) + 1
    log.append({
        "step": step_num,
        "phase": "trace_check",
        "success": reached,
        "trace": trace,
    })
    save_log(log)

    print(f"[Step {step_num}] target branch reached = {reached}")
    print("-" * 50)
    print(trace)
    print("-" * 50)

    if reached:
        print("Đã tới target branch. Ground-truth trace sẵn sàng trong visited_trace.txt.")
        return

    print("Chưa tới target branch. Đang tạo reflection_prompt.txt...")
    with open(DRIVER_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    template = load_prompt_template("prompt_trace_reflection.txt")
    reflection_prompt = template.format(
        target_branch=CONFIG["target_branch"],
        previous_code=code,
        visited_trace=trace,
    )
    with open("reflection_prompt.txt", "w", encoding="utf-8") as f:
        f.write(reflection_prompt)

    print("Saved reflection_prompt.txt — copy vào LLM, paste kết quả vào response.txt, "
          "rồi chạy lại step2_compile.py -> step3_trace.py")


if __name__ == "__main__":
    main()