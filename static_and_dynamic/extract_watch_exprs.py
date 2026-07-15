# extract_watch_exprs.py
"""
Automatically extracts variable/member-access expressions from a target function's
AST so GDB can watch them, without hardcoding a watch-list by hand.
Supports both single-line and multi-line expressions (e.g. e->vState[e->vState.size() - 2]).
"""
import clang.cindex
import json

clang.cindex.Config.set_library_file(r"E:\Programs\Python312\Lib\site-packages\clang\native\libclang.dll")

WATCHABLE_KINDS = {
    clang.cindex.CursorKind.MEMBER_REF_EXPR,
    clang.cindex.CursorKind.DECL_REF_EXPR,
}
GETTER_CALL_NAMES = {"type", "size", "empty", "begin", "end"}


def get_source_text(node, source_lines):
    """Extract exact source text for a node, supporting expressions spanning multiple lines."""
    start = node.extent.start
    end = node.extent.end

    if start.line == end.line:
        line = source_lines[start.line - 1]
        return line[start.column - 1:end.column - 1]

    # Multi-line expression: join first partial line, full middle lines, last partial line
    parts = []
    first_line = source_lines[start.line - 1]
    parts.append(first_line[start.column - 1:])

    for lineno in range(start.line, end.line - 1):
        parts.append(source_lines[lineno])

    last_line = source_lines[end.line - 1]
    parts.append(last_line[:end.column - 1])

    text = "".join(parts)
    # Collapse internal newlines/whitespace so GDB parse_and_eval gets a single valid expression
    return " ".join(text.split())


def extract_watch_exprs(file_path, target_function):
    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=