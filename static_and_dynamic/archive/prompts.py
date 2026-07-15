# prompts.py
"""
Prompt templates for the LLM-driven test generation + compile-fix + trace-reflection loop.
"""

PROMPT_INITIAL = r"""
You are an expert C++ software engineer. Your task is to write a standalone `test_main.cpp` file to test a specific branch inside a target function.

### CONTEXT
The following context contains the exact definitions of the structs, classes, enums, and the focal function you need. It has been pre-extracted for you:
{context}

### OBJECTIVE
Target Function: {focal_function}
Target Branch/Line to Cover: {target_branch}

### INSTRUCTIONS
1. Analyze the Context to understand the data structures required by the Target Function.
2. Write a `main()` function that initializes the required arguments (e.g., pointers, objects, vectors) properly to avoid segmentation faults.
3. Set the state of these objects specifically to force the execution flow into the Target Branch.
4. The code must be compilable. Include `<iostream>` and assume `#include "hjson.h"` is available.
5. Do NOT provide any explanations.
6. Return exactly one Markdown code block containing the complete C++ source code.
"""

PROMPT_COMPILATION_FIX = r"""
You are a C++ debugging expert. The generated test driver failed to compile.

### PREVIOUS CODE
{previous_code}

### COMPILER ERRORS
{compiler_errors}

### CONTEXT REFERENCE
{context}

### INSTRUCTIONS
1. Analyze the compiler errors. Common causes include missing initializations, private access violations, incorrect API usage, or missing headers.
2. Fix the C++ code so that it compiles successfully while still attempting to reach the original target branch.
3. Do NOT change the overall testing objective unless required to make the code compile.
4. Do NOT provide any explanations.
5. Return exactly one Markdown code block containing the complete corrected C++ source code.
"""

PROMPT_TRACE_REFLECTION = r"""
You are an expert C++ dynamic analysis engineer. Your previous test driver compiled successfully, but it failed to reach the intended target branch during runtime.

### TARGET BRANCH
{target_branch}

### PREVIOUS CODE
{previous_code}

### DYNAMIC EXECUTION TRACE
The following execution trace shows exactly what happened during runtime, including the local-variable state changes (State Diff):
{visited_trace}

### INSTRUCTIONS
1. Analyze the execution trace to determine where execution diverged from the intended target branch.
2. Identify which condition evaluated differently than expected and which variable values caused the divergence.
3. Modify only the object initialization and input construction in the previous test driver to satisfy the required branch conditions.
4. Preserve as much of the previous test driver as possible.
5. Do NOT provide any explanations.
6. Return exactly one Markdown code block containing the complete revised C++ source code.
"""