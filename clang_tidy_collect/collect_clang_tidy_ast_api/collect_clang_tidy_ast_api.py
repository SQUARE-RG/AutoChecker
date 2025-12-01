import os
import json
import clang.cindex
#usage:  /usr/bin/python clang_tidy_collect/collect_clang_tidy_ast_api/collect_clang_tidy_ast_api.py
def get_namespace_path(cursor):
    # 递归获取命名空间全称（包括嵌套）
    ns = []
    cur = cursor.semantic_parent
    while cur:
        if cur.kind == clang.cindex.CursorKind.NAMESPACE:
            ns.insert(0, cur.spelling)
        cur = cur.semantic_parent
    return "::".join(ns) if ns else ""

def extract_class_or_struct_info(cursor):
    # 提取类或结构体信息
    ns_full = get_namespace_path(cursor) # 获取完全限定的命名空间路径
    name = cursor.spelling  # 类/结构体名称
    is_struct = cursor.kind == clang.cindex.CursorKind.STRUCT_DECL # 判断是否为结构体
    
    # 继承
    # 遍历所有子节点，找到基类（CXX_BASE_SPECIFIER类型的节点）。
    extends = []
    for base in cursor.get_children():
        if base.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
            extends.append(base.type.spelling)
    
    # 成员和方法
    methods = []
    fields = []
    # 结构体默认public，类默认private
    current_access = "public" if is_struct else "private"
    
    # 遍历所有子节点
    for child in cursor.get_children():
        # 处理访问修饰符
        # 处理访问修饰符（public:/private:/protected:）
        # 遇到CXX_ACCESS_SPEC_DECL节点（如public:）时，更新current_access
        if child.kind == clang.cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
            # 方法 1：使用 displayname
            # current_access = child.displayname.rstrip(':')
            # 方法 2：使用 tokens
            tokens = list(child.get_tokens())
            if tokens and tokens[0].spelling in ("public", "private", "protected"):
                current_access = tokens[0].spelling
            # print(f"Access specifier: {current_access} for {name} in {ns_full}")
            continue
            
        # 只处理public成员
        if current_access != "public":
            continue
            
        if child.kind == clang.cindex.CursorKind.CXX_METHOD:

            args = [{"name": arg.spelling, "type": arg.type.spelling}
                    for arg in child.get_arguments()]
            arg_str = ", ".join([f"{a['type']} {a['name']}" if a['name'] else a['type'] for a in args])

            # 方法全名（带命名空间和类名）
            ns_prefix = ns_full + "::" if ns_full else ""
            class_prefix = name + "::" if child.semantic_parent.spelling == name else ""
            method_name = child.spelling

            # 构造/析构函数特殊处理
            if child.kind == clang.cindex.CursorKind.CONSTRUCTOR:
                signature = f"{ns_prefix}{name}::{name}({arg_str})"
            elif child.kind == clang.cindex.CursorKind.DESTRUCTOR:
                signature = f"{ns_prefix}{name}::~{name}({arg_str})"
            else:
            # 普通成员函数
                signature = f"{child.result_type.spelling} {ns_prefix}{class_prefix}{method_name}({arg_str})"
            if child.is_const_method():
                signature += " const"
            method = {
                "name": child.spelling,
                "returnType": child.result_type.spelling,
                "args": [
                    {"name": arg.spelling, "type": arg.type.spelling}
                    for arg in child.get_arguments()
                ],
                "method_signature": signature
            }
            methods.append(method)
        elif child.kind == clang.cindex.CursorKind.FIELD_DECL:
            field = {
                "name": child.spelling,
                "type": child.type.spelling,
                "access": current_access
            }
            fields.append(field)
    
    return {
        "namespace": ns_full,
        "name": name,
        "isStruct": is_struct,
        "extends": extends,
        "methods": methods,
        "fields": fields
    }

def process_header(filepath, class_list, struct_list, seen):
    index = clang.cindex.Index.create()
    tu = index.parse(filepath, args=[
        "-std=c++17",
        "-I/root/code_check/llvm-project/clang/include",
        "-I/root/code_check/llvm-project/llvm/include",
        "-I/usr/include",
        "-x", "c++"
    ])
    for cursor in tu.cursor.get_children():
        collect_classes_and_structs(cursor, class_list, struct_list, seen)

def collect_classes_and_structs(cursor, class_list, struct_list, seen):
    # 递归收集所有类和结构体
    if (cursor.kind == clang.cindex.CursorKind.CLASS_DECL or 
        cursor.kind == clang.cindex.CursorKind.STRUCT_DECL) and cursor.is_definition():
        
        info = extract_class_or_struct_info(cursor)
        key = (info["namespace"], info["name"])
        
        if key in seen:
            # 合并同名类/结构体（命名空间相同）
            existing = seen[key]
            for e in info["extends"]:
                if e not in existing["extends"]:
                    existing["extends"].append(e)
            for m in info["methods"]:
                if not any(mm["name"] == m["name"] for mm in existing["methods"]):
                    existing["methods"].append(m)
            for f in info["fields"]:
                if not any(ff["name"] == f["name"] for ff in existing["fields"]):
                    existing["fields"].append(f)
        else:
            if info["isStruct"]:
                struct_list.append(info)
            else:
                class_list.append(info)
            seen[key] = info
    
    for child in cursor.get_children():
        collect_classes_and_structs(child, class_list, struct_list, seen)

def main():
    clang.cindex.Config.set_library_file('/usr/local/lib/python3.10/dist-packages/clang/native/libclang.so')

    # clang.cindex.Config.set_library_file('/usr/lib/llvm-14/lib/libclang.so')
    ast_dir = "/root/code_check/llvm-project/clang/include/clang/AST"
    output_json = "/root/code_check/clang_tidy_collect/collect_clang_tidy_ast_api/clang_tidy_ast_api.json"
    basic_dir = "/root/code_check/llvm-project/clang/include/clang/Basic"
    analysize_dir ="/root/code_check/llvm-project/clang/include/clang/Analysis"
    class_list = []
    struct_list = []
    seen = {}
    
    for fname in os.listdir(ast_dir):
        if fname.endswith(".h"):
            fpath = os.path.join(ast_dir, fname)
            try:
                process_header(fpath, class_list, struct_list, seen)
                print(f"Processed {fpath}")
            except Exception as e:
                print(f"Failed to parse {fpath}: {e}")
    
    for fname in os.listdir(basic_dir):
        if fname.endswith(".h"):
            fpath = os.path.join(basic_dir, fname)
            try:
                process_header(fpath, class_list, struct_list, seen)
                print(f"Processed {fpath}")
            except Exception as e:
                print(f"Failed to parse {fpath}: {e}")
    for fname in os.listdir(analysize_dir):
        if fname.endswith(".h"):
            fpath = os.path.join(analysize_dir, fname)
            try:
                process_header(fpath, class_list, struct_list, seen)
                print(f"Processed {fpath}")
            except Exception as e:
                print(f"Failed to parse {fpath}: {e}")
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "class": class_list,
            "struct": struct_list
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Saved AST info to {output_json}")

if __name__ == "__main__":
    main()
