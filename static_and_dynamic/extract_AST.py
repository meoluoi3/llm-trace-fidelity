# extract_AST.py
"""
Extracts static context (enums, structs/classes, target function body) from source code
via clang AST, and returns it as a string usable inside LLM prompts.
"""
import clang.cindex
import os

clang.cindex.Config.set_library_file(r"E:\Programs\Python312\Lib\site-packages\clang\native\libclang.dll")


def get_context(file_path, target_function):
    """Returns the extracted static context as a single string (for prompt injection)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    index = clang.cindex.Index.create()
    translation_unit = index.parse(file_path, args=['-x', 'c++', '-std=c++11', '-Wno-everything'])

    with open(file_path, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()

    ast = []

    def get_source_block(node):
        start = node.extent.start.line - 1
        end = node.extent.end.line
        return "".join(source_lines[start:end])

    def visit_node(node):
        if node.location.file and node.location.file.name == translation_unit.spelling:
            if node.kind == clang.cindex.CursorKind.ENUM_DECL:
                ast.append(f"// --- {node.kind.name}: {node.spelling} ---\n" + get_source_block(node))
            elif node.kind in [clang.cindex.CursorKind.CLASS_DECL, clang.cindex.CursorKind.STRUCT_DECL]:
                ast.append(f"// --- Class/Struct: {node.spelling} ---\n" + get_source_block(node))
            elif node.kind == clang.cindex.CursorKind.FUNCTION_DECL and node.spelling == target_function:
                ast.append(f"// --- Function: {node.spelling} ---\n" + get_source_block(node))

        for child in node.get_children():
            visit_node(child)

    visit_node(translation_unit.cursor)
    return "\n".join(ast)


def save_context_to_file(file_path, target_function, output_dir="."):
    context = get_context(file_path, target_function)
    base_file_name = os.path.basename(file_path).replace(".cpp", "")
    output_filename = os.path.join(output_dir, f"{base_file_name}_{target_function}.txt")
    with open(output_filename, "w", encoding="utf-8") as out_file:
        out_file.write(context)
    return context


if __name__ == "__main__":
    ctx = save_context_to_file("../hjson-cpp/src/hjson_encode.cpp", "_writeValueBegin")
    print(ctx)