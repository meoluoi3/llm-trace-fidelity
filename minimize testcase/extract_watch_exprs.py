import clang.cindex
import json

clang.cindex.Config.set_library_file(r"E:\Programs\Python312\Lib\site-packages\clang\native\libclang.dll")

WATCHABLE_KINDS = {
    clang.cindex.CursorKind.MEMBER_REF_EXPR,
    clang.cindex.CursorKind.DECL_REF_EXPR,
}
GETTER_CALL_NAMES = {"type", "size", "empty", "begin", "end"}

def get_source_text(node, source_lines):
    start = node.extent.start
    end = node.extent.end

    if start.line == end.line:
        line = source_lines[start.line - 1]
        return line[start.column - 1:end.column - 1]

    parts = []
    first_line = source_lines[start.line - 1]
    parts.append(first_line[start.column - 1:])

    for lineno in range(start.line, end.line - 1):
        parts.append(source_lines[lineno])

    last_line = source_lines[end.line - 1]
    parts.append(last_line[:end.column - 1])

    text = "".join(parts)
    return " ".join(text.split())

def extract_watch_exprs(file_path, target_function):
    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=['-x', 'c++', '-std=c++11', '-Wno-everything'])

    with open(file_path, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()

    exprs = set()

    def find_function_node(node):
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL and node.spelling == target_function:
            return node
        for child in node.get_children():
            found = find_function_node(child)
            if found:
                return found
        return None

    func_node = find_function_node(tu.cursor)
    if func_node is None:
        raise ValueError(f"Function '{target_function}' not found in {file_path}")

    def visit(node):
        is_function_ref = False
        if node.referenced:
            if node.referenced.kind in [
                clang.cindex.CursorKind.CXX_METHOD,
                clang.cindex.CursorKind.FUNCTION_DECL,
                clang.cindex.CursorKind.FUNCTION_TEMPLATE
            ]:
                is_function_ref = True

        if node.kind in WATCHABLE_KINDS and not is_function_ref:
            text = get_source_text(node, source_lines)
            if text and text.strip():
                if not text.startswith("std::") and not text.startswith("_quote"):
                   exprs.add(text.strip())

        if node.kind == clang.cindex.CursorKind.CALL_EXPR and node.spelling in GETTER_CALL_NAMES:
            text = get_source_text(node, source_lines)
            if text and text.strip():
                clean_text = text.strip()
                if not clean_text.endswith(")"):
                    clean_text += "()"
                exprs.add(text.strip())

        for child in node.get_children():
            visit(child)

    visit(func_node)
    cleaned = sorted(e for e in exprs if e and not e[0].isdigit())
    return cleaned

def save_watch_exprs(file_path, target_function, output_path="watch_exprs.json"):
    watch_list = extract_watch_exprs(file_path, target_function)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(watch_list, f, indent=2, ensure_ascii=False)
    return watch_list

if __name__ == "__main__":
    watch_list = save_watch_exprs("../hjson-cpp/src/hjson_encode.cpp", "_writeValueBegin")
    print(f"Extracted {len(watch_list)} watch expressions.")