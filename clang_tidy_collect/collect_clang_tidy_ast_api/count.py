import json

# 1129个class

def main():
    with open("/root/code_check/clang_tidy_collect/collect_clang_tidy_ast_api/clang_tidy_ast_api.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    classes = data.get("class", [])
    num_class = len(classes)
    num_method = sum(len(c.get("methods", [])) for c in classes)
    num_field = sum(len(c.get("fields", [])) for c in classes)
    print(f"Class count: {num_class}")
    print(f"Method count: {num_method}")
    print(f"Field count: {num_field}")

    structs = data.get("struct", [])
    num_struct = len(structs)
    num_method = sum(len(c.get("methods", [])) for c in structs)
    num_field = sum(len(c.get("fields", [])) for c in structs)
    print(f"structs count: {num_struct}")
    print(f"Method count: {num_method}")
    print(f"Field count: {num_field}")

if __name__ == "__main__":
    main()
