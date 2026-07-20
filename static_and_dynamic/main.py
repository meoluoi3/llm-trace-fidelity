import subprocess
import os
import glob

def main():
    print("=== LLM Trace Fidelity ===")
    
    # ==========================================
    # 1: TEST DRIVER
    # ==========================================
    # LLM generated test driver code for hjson-cpp
    # print("creating test_main.cpp for LLM-generated test driver...")
    
    # # with open("test_main.cpp", "w", encoding="utf-8") as f:
    # #     f.write(test_code)
    # print("created test_main.cpp for LLM-generated test driver.")

    # ==========================================
    # 2: compile the test driver with hjson-cpp
    # ==========================================
    print("compiling test_main.cpp with hjson-cpp...")
    
    all_cpp_files = glob.glob("../hjson-cpp/src/*.cpp")
    
    # Filter out hjson_encode.cpp from the compilation list to avoid multiple definitions
    # since it is included directly in the test driver.
    cpp_files = [f for f in all_cpp_files if "hjson_encode.cpp" not in f.replace('\\', '/')]
    
    compile_cmd = [
        "g++", "-g", "-O0", 
        "gptdouble3rd.cpp"
    ] + cpp_files + [
        "-I", "../hjson-cpp/include/hjson", 
        "-o", "target.exe"
    ]

    compile_result = subprocess.run(compile_cmd, capture_output=True, text=True)
    
    if compile_result.returncode != 0:
        print("compilation failed with errors:")
        print(compile_result.stderr)
        return # Stop execution if compilation fails
        
    print("successfully compiled test driver with hjson-cpp into 'target.exe' executable.")

    # ==========================================
    #  3: run GDB tracer on the compiled target
    # ==========================================
    print("running GDB tracer on the compiled target...")
    
    # Remove old trace file (if it exists) to avoid messy overwrites
    if os.path.exists("visited_trace.txt"):
        os.remove("visited_trace.txt")

    run_cmd = [
        "gdb", "-q", "--batch",
        "-x", "gdb_tracer.py",
        "--args", "./target.exe"
    ]
    
    result = subprocess.run(run_cmd, capture_output=True, text=True)

    print(result.stdout)
    print(result.stderr)

    # ==========================================
    #  4: read the trace log and print it for LLM to read
    # ==========================================
    if os.path.exists("visited_trace.txt"):
        with open("visited_trace.txt", "r", encoding="utf-8") as f:
            trace_content = f.read()
            
        print("successfully ran GDB tracer\n")
        print("-" * 50)
        print("=== GDB Execution Trace ===")
        print("-" * 50)
        print(trace_content)
        print("-" * 50)
    else:
        print("Error: visited_trace.txt not found. GDB tracer may have failed.")

if __name__ == "__main__":
    main()