import clang.cindex
import os
clang.cindex.Config.set_library_file(r"E:\Programs\Python312\Lib\site-packages\clang\native\libclang.dll")

def extract_ast(file_path, target_function):
    if not os.path.exists(file_path):
        return FileNotFoundError(f"The file {file_path} does not exist.")
    
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

zuzu = extract_ast("../hjson-cpp/src/hjson_encode.cpp", "_writeValueBegin")

if isinstance(zuzu, str): 
    base_file_name = os.path.basename("../hjson-cpp/src/hjson_encode.cpp").replace(".cpp", "") 
    output_filename = f"{base_file_name}_{'_writeValueBegin'}.txt" 
    with open(output_filename, "w", encoding="utf-8") as out_file: 
        out_file.write(zuzu) 

print(zuzu)