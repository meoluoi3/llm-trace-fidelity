# step1_prepare.py
import json
from extract_AST import get_context
from extract_watch_exprs import save_watch_exprs

CONFIG = {
    "source_file": "../hjson-cpp/src/hjson_encode.cpp",
    "target_function": "_writeValueBegin",
    "target_branch": "case Type::Map: (the branch handling Hjson::Type::Map values)",
}

def load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    print("Extracting static context via clang AST...")
    context = get_context(CONFIG["source_file"], CONFIG["target_function"])

    print("Extracting GDB watch expressions via AST...")
    save_watch_exprs(CONFIG["source_file"], CONFIG["target_function"])

    template = load_prompt_template("prompt_initial.txt")
    prompt = template.format(
        context=context,
        focal_function=CONFIG["target_function"],
        target_branch=CONFIG["target_branch"],
    )

    with open("prompt_out.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    with open("run_config.json", "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=2, ensure_ascii=False)

    print("Saved prompt_out.txt — copy nội dung này vào LLM.")
    print("Paste code trả về vào response.txt rồi chạy step2_compile.py")

if __name__ == "__main__":
    main()