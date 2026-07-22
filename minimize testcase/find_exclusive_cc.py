import clang.cindex
import glob
import json
import sys
import os

clang.cindex.Config.set_library_file(r"E:\Programs\Python312\Lib\site-packages\clang\native\libclang.dll")

SEQUENTIAL_KINDS = {
    clang.cindex.CursorKind.WHILE_STMT,
    clang.cindex.CursorKind.DO_STMT,
    clang.cindex.CursorKind.FOR_STMT,
}


def count_switch_cases(node):
    count = 0
    for child in node.get_children():
        if child.kind in (clang.cindex.CursorKind.CASE_STMT, clang.cindex.CursorKind.DEFAULT_STMT):
            count += 1
        count += count_switch_cases(child)
    return count


def has_else_branch(if_node) -> bool:
    children = list(if_node.get_children())
    return len(children) >= 3


def analyze_function(func_node):
    switch_count = 0
    switch_total_cases = 0
    if_else_count = 0
    guard_if_count = 0
    loop_count = 0

    def visit(node):
        nonlocal switch_count, switch_total_cases, if_else_count, guard_if_count, loop_count

        if node.kind == clang.cindex.CursorKind.SWITCH_STMT:
            switch_count += 1
            switch_total_cases += count_switch_cases(node)

        if node.kind == clang.cindex.CursorKind.IF_STMT:
            if has_else_branch(node):
                if_else_count += 1
            else:
                guard_if_count += 1

        if node.kind in SEQUENTIAL_KINDS:
            loop_count += 1

        for child in node.get_children():
            visit(child)

    visit(func_node)

    exclusive_points = switch_total_cases + if_else_count
    sequential_points = guard_if_count + loop_count
    total_points = exclusive_points + sequential_points

    exclusivity_ratio = exclusive_points / total_points if total_points > 0 else 0.0

    return {
        "switch_count": switch_count,
        "switch_total_cases": switch_total_cases,
        "if_else_count": if_else_count,
        "guard_if_count": guard_if_count,
        "loop_count": loop_count,
        "exclusive_points": exclusive_points,
        "sequential_points": sequential_points,
        "exclusivity_ratio": round(exclusivity_ratio, 3),
    }


def scan_file(file_path):
    results = []
    try:
        index = clang.cindex.Index.create()
        tu = index.parse(file_path, args=['-x', 'c++', '-std=c++11', '-Wno-everything'])
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return results

    def visit(node):
        if node.location.file and node.location.file.name == tu.spelling:
            if node.kind in (clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD) and node.is_definition():
                stats = analyze_function(node)
                start = node.extent.start.line
                end = node.extent.end.line
                results.append({
                    "function": node.spelling,
                    "file": file_path,
                    "loc": end - start + 1,
                    "start_line": start,
                    "end_line": end,
                    **stats,
                })
        for child in node.get_children():
            visit(child)

    visit(tu.cursor)
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_exclusive_cc.py <file.cpp or folder_path>")
        sys.exit(1)

    target_path = sys.argv[1]
    all_files = []

    if os.path.isfile(target_path):
        all_files = [target_path]
    elif os.path.isdir(target_path):
        all_files = glob.glob(os.path.join(target_path, "*.cpp"))
    else:
        print(f"Error: Path '{target_path}' is invalid or does not exist.")
        sys.exit(1)

    all_results = []
    for f in all_files:
        all_results.extend(scan_file(f))

    all_results = [r for r in all_results if r["exclusive_points"] + r["sequential_points"] > 0]
    all_results.sort(key=lambda r: (r["exclusivity_ratio"], r["exclusive_points"]), reverse=True)

    print(f"{'Ratio':>6} {'ExclPts':>8} {'SeqPts':>7} {'Switch':>7} {'IfElse':>7} {'GuardIf':>8} {'Loop':>5} {'LOC':>5}  Function (file)")
    print("-" * 110)
    for r in all_results[:25]:
        print(f"{r['exclusivity_ratio']:>6} {r['exclusive_points']:>8} {r['sequential_points']:>7} "
              f"{r['switch_count']:>7} {r['if_else_count']:>7} {r['guard_if_count']:>8} {r['loop_count']:>5} "
              f"{r['loc']:>5}  {r['function']} ({r['file']})")
              
    os.makedirs("./cc_results", exist_ok=True)
    with open("./cc_results/exclusive_cc_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_results)} functions to ./cc_results/exclusive_cc_results.json")


if __name__ == "__main__":
    main()