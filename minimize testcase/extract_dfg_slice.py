import clang.cindex
import sys
import re
import json

clang.cindex.Config.set_library_file(r"E:\Programs\Python312\Lib\site-packages\clang\native\libclang.dll")

ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="}
COMPARISON_OPS = {"==", "!=", "<", ">", "<=", ">=", "&&", "||"}


def normalize_expr(text: str) -> str:
    text = text.strip().replace("->", ".")
    return re.sub(r"\s+", "", text)


def get_source_text(node, source_lines):
    start = node.extent.start
    end = node.extent.end
    if start.line == end.line:
        return source_lines[start.line - 1][start.column - 1:end.column - 1]
    parts = [source_lines[start.line - 1][start.column - 1:]]
    for lineno in range(start.line, end.line - 1):
        parts.append(source_lines[lineno])
    parts.append(source_lines[end.line - 1][:end.column - 1])
    return " ".join("".join(parts).split())


def collect_identifiers(node, source_lines, out_set):
    if node.kind in (clang.cindex.CursorKind.MEMBER_REF_EXPR, clang.cindex.CursorKind.DECL_REF_EXPR):
        text = get_source_text(node, source_lines)
        if text:
            out_set.add(normalize_expr(text))

    children = list(node.get_children())

    if node.kind == clang.cindex.CursorKind.UNEXPOSED_EXPR or not children:
        try:
            for token in node.get_tokens():
                if token.kind == clang.cindex.TokenKind.IDENTIFIER:
                    out_set.add(token.spelling)
        except Exception:
            pass

    for child in children:
        collect_identifiers(child, source_lines, out_set)


def get_statement_line_range(node):
    return node.extent.start.line, node.extent.end.line


def is_assignment_operator(node) -> bool:
    tokens = [t.spelling for t in node.get_tokens()]
    for tok in tokens:
        if tok in ASSIGN_OPS:
            return True
        if tok in COMPARISON_OPS:
            return False
    return False


def build_parent_map(node, parent_map, parent=None):
    if parent is not None:
        parent_map[node.hash] = parent
    for child in node.get_children():
        build_parent_map(child, parent_map, node)


def get_nearest_branch_id(node, parent_map, func_hash):
    if node is None:
        return None
    current = node
    while True:
        if current.hash not in parent_map:
            return None
        parent = parent_map[current.hash]
        if parent.hash == func_hash:
            return None
        if parent.kind in (clang.cindex.CursorKind.CASE_STMT, clang.cindex.CursorKind.DEFAULT_STMT):
            return ("case", parent.hash)
        if parent.kind == clang.cindex.CursorKind.IF_STMT:
            children = list(parent.get_children())
            if len(children) >= 2 and children[1].hash == current.hash:
                return ("if_then", parent.hash)
            if len(children) >= 3 and children[2].hash == current.hash:
                return ("if_else", parent.hash)
        current = parent


def backward_slice(file_path, target_function, target_line):
    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=['-x', 'c++', '-std=c++11', '-Wno-everything'])

    with open(file_path, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()

    def find_function_node(node):
        if node.kind in (clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD) and node.is_definition() and node.spelling == target_function:
            return node
        for child in node.get_children():
            result = find_function_node(child)
            if result:
                return result
        return None

    func_node = find_function_node(tu.cursor)
    if func_node is None:
        raise ValueError(f"Function '{target_function}' not found in {file_path}")

    parent_map = {}
    build_parent_map(func_node, parent_map)

    statements = []
    STATEMENT_KINDS = {
        clang.cindex.CursorKind.DECL_STMT,
        clang.cindex.CursorKind.BINARY_OPERATOR,
        clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR,
        clang.cindex.CursorKind.UNARY_OPERATOR,
        clang.cindex.CursorKind.CALL_EXPR,
        clang.cindex.CursorKind.IF_STMT,
        clang.cindex.CursorKind.SWITCH_STMT,
    }

    def collect_statements(node):
        for child in node.get_children():
            if child.kind in STATEMENT_KINDS:
                statements.append(child)
            collect_statements(child)

    collect_statements(func_node)

    CONTAINER_KINDS = {
        clang.cindex.CursorKind.IF_STMT,
        clang.cindex.CursorKind.SWITCH_STMT,
    }

    relevant = set()
    target_stmt = None
    for stmt in statements:
        start_line, end_line = get_statement_line_range(stmt)

        if target_line == 0:
            if stmt.kind in CONTAINER_KINDS:
                children = list(stmt.get_children())
                if children:
                    collect_identifiers(children[0], source_lines, relevant)
        elif start_line <= target_line <= end_line:
            if stmt.kind in CONTAINER_KINDS:
                children = list(stmt.get_children())
                if children:
                    collect_identifiers(children[0], source_lines, relevant)
            else:
                collect_identifiers(stmt, source_lines, relevant)
                if start_line == end_line == target_line:
                    target_stmt = stmt

    if not relevant:
        raise ValueError(f"No relevant identifiers found at line {target_line} in function '{target_function}'")

    seed = set(relevant)
    print(f"Initial relevant identifiers at line {target_line}: {seed}")

    target_branch = None
    if target_line != 0 and target_stmt is not None:
        target_branch = get_nearest_branch_id(target_stmt, parent_map, func_node.hash)
        print(f"Target branch scope: {target_branch}")

    statements_before = [s for s in statements if get_statement_line_range(s)[1] < target_line]
    statements_before.sort(key=lambda s: get_statement_line_range(s)[0], reverse=True)

    for stmt in statements_before:
        if target_line != 0:
            stmt_branch = get_nearest_branch_id(stmt, parent_map, func_node.hash)
            if stmt_branch is not None and stmt_branch != target_branch:
                continue

        if stmt.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
            if not is_assignment_operator(stmt):
                continue
            children = list(stmt.get_children())
            if len(children) == 2:
                lhs, rhs = children
                lhs_vars = set()
                collect_identifiers(lhs, source_lines, lhs_vars)
                if lhs_vars & relevant:
                    collect_identifiers(rhs, source_lines, relevant)

        elif stmt.kind == clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
            children = list(stmt.get_children())
            if len(children) == 2:
                lhs, rhs = children
                lhs_vars = set()
                collect_identifiers(lhs, source_lines, lhs_vars)
                if lhs_vars & relevant:
                    collect_identifiers(rhs, source_lines, relevant)

        elif stmt.kind == clang.cindex.CursorKind.UNARY_OPERATOR:
            operand_vars = set()
            collect_identifiers(stmt, source_lines, operand_vars)
            if operand_vars & relevant:
                relevant |= operand_vars

        elif stmt.kind == clang.cindex.CursorKind.DECL_STMT:
            start_l = stmt.extent.start.line
            raw_line_text = source_lines[start_l - 1]

            for child in stmt.get_children():
                if child.kind == clang.cindex.CursorKind.VAR_DECL:
                    declared_name = normalize_expr(child.spelling) if child.spelling else ""
                    if declared_name in relevant:
                        init_vars = set()

                        for init_child in child.get_children():
                            collect_identifiers(init_child, source_lines, init_vars)

                        if not init_vars and "=" in raw_line_text:
                            rhs_str = raw_line_text.split("=", 1)[1]
                            # giữ nguyên cụm dạng a->b.c() thay vì tách rời từng từ
                            member_chains = re.findall(r'[a-zA-Z_]\w*(?:(?:->|\.)[a-zA-Z_]\w*(?:\(\))?)*', rhs_str)
                            ignore_words = {"new", "const", "static", "true", "false", "nullptr"}
                            for chain in member_chains:
                                base = chain.split("->")[0].split(".")[0]
                                if base not in ignore_words and chain.strip():
                                    init_vars.add(normalize_expr(chain))

                        if init_vars:
                            relevant |= init_vars

    return {"target_line": target_line, "seed_vars": sorted(seed), "relevant_vars": sorted(relevant)}


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python extract_dfg_slice.py <file.cpp> <target_function> <target_line>")
        sys.exit(1)

    file_path, target_function, target_line = sys.argv[1], sys.argv[2], int(sys.argv[3])
    result = backward_slice(file_path, target_function, target_line)

    output_path = f"dfg_slice_line{target_line}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Saved to {output_path}")