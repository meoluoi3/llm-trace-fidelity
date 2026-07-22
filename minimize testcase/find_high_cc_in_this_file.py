# Count every decision point in a function ( if, for, while, case, catch, &&, || )
import clang.cindex
import glob
import json
import sys
import os

clang.cindex.Config.set_library_file(r"E:\Programs\Python312\Lib\site-packages\clang\native\libclang.dll")

DECISION_KINDS = {
    clang.cindex.CursorKind.IF_STMT,
    clang.cindex.CursorKind.FOR_STMT,
    clang.cindex.CursorKind.WHILE_STMT,
    clang.cindex.CursorKind.DO_STMT,
    clang.cindex.CursorKind.CASE_STMT,
    clang.cindex.CursorKind.DEFAULT_STMT,
    clang.cindex.CursorKind.CONDITIONAL_OPERATOR,  
    clang.cindex.CursorKind.CXX_CATCH_STMT,        
}

LOGICAL_OPERATORS = {
    '&&',
    '||',
}

def count_cc(func_node):
    cc = 1 # CC = decision points + 1
    def visit (node):
        nonlocal cc
        if node.kind in DECISION_KINDS:
            cc += 1
        if node.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
            tokens = [t.spelling for t in node.get_tokens()]
            if any(t in LOGICAL_OPERATORS for t in tokens):
                cc += 1
        
        for child in node.get_children():
            visit(child)
    visit(func_node)
    return cc

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
                cc = count_cc(node)
                start = node.extent.start.line
                end = node.extent.end.line
                results.append({
                        "function": node.spelling,
                        "file": file_path,
                        "cc": cc,
                        "start_line": start,
                        "end_line": end,
                        "loc": end - start + 1,
                    })
        for child in node.get_children():
            visit(child)
    visit(tu.cursor)
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python find_high_cc.py <file.cpp or folder_path>")
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

    all_results.sort(key=lambda r: r["cc"], reverse=True)

    print(f"{'CC':>4} {'LOC':>5}  Function (file)")
    print("-" * 70)
    for r in all_results[:20]:
        print(f"{r['cc']:>4} {r['loc']:>5}  {r['function']} ({r['file']})")

    os.makedirs("./cc_results", exist_ok=True)
    with open("./cc_results/cc_scan_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nSaving {len(all_results)} functions to ./cc_results/cc_scan_results.json")

if __name__ == "__main__":
    main()