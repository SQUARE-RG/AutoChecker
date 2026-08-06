#!/usr/bin/env python3

import os
import io
import sys
import argparse
import re

def get_camel_name(check_name):
    return "".join(map(lambda elem: elem.capitalize(), check_name.split("-")))

def get_camel_check_name(check_name):
    return get_camel_name(check_name) + "Check"

def get_module_filename(module_path, module):
    for p in os.listdir(module_path):
        if p.lower() == module.lower() + "tidymodule.cpp":
            return os.path.join(module_path, p)
    return None

def remove_file(filepath):
    if os.path.isfile(filepath):
        print(f"Removing {filepath}")
        os.remove(filepath)

def remove_line_from_file(filepath, pattern):
    if not os.path.isfile(filepath):
        return
    with io.open(filepath, "r", encoding="utf8") as f:
        lines = f.readlines()
    with io.open(filepath, "w", encoding="utf8", newline="\n") as f:
        for line in lines:
            if not re.search(pattern, line):
                f.write(line)

def remove_multiline_register_check(filepath, check_name_camel, module, check_name):
    if not os.path.isfile(filepath):
        return
    with io.open(filepath, "r", encoding="utf8") as f:
        lines = f.readlines()
    # 更宽松的正则，允许任意空白、换行、参数分行
    # 例：CheckFactories.registerCheck<AutotestCheck>( "ucassaat-AutoTest");
    pattern = re.compile(
        r'CheckFactories\s*\.\s*registerCheck\s*<\s*%s\s*>\s*\(' % re.escape(check_name_camel),
        re.IGNORECASE
    )
    arg_pattern = re.compile(
        r'"\s*%s-%s\s*"' % (re.escape(module), re.escape(check_name)),
        re.IGNORECASE
    )
    out_lines = []
    skip = False
    found = False
    for idx, line in enumerate(lines):
        if not skip and pattern.search(line):
            # 进入 registerCheck 匹配，查找参数行
            found = True
            skip = True
            continue
        if skip:
            # 跳过直到遇到参数和 );
            if arg_pattern.search(line):
                # 继续跳过直到遇到 );
                if line.rstrip().endswith(");"):
                    skip = False
                continue
            elif line.rstrip().endswith(");"):
                skip = False
                continue
            else:
                continue
        out_lines.append(line)
    with io.open(filepath, "w", encoding="utf8", newline="\n") as f:
        f.writelines(out_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="module directory under which the tidy check is placed (e.g., misc)")
    parser.add_argument("check", help="name of tidy check to remove (e.g. foo-do-the-stuff)")
    args = parser.parse_args()

    module = args.module
    check_name = args.check
    check_name_camel = get_camel_check_name(check_name)
    clang_tidy_path = os.path.dirname(sys.argv[0])
    module_path = os.path.join(clang_tidy_path, module)
    # print(f"Removing check {check_name} from module {module_path}...")

    # 1. 删除 .cpp/.h
    remove_file(os.path.join(module_path, check_name_camel + ".cpp"))
    remove_file(os.path.join(module_path, check_name_camel + ".h"))

    # 2. 删除测试文件
    test_dir = os.path.normpath(os.path.join(module_path, "..", "..", "test", "clang-tidy", "checkers", module))
    for ext in ["cpp", "c", "m", "mm"]:
        remove_file(os.path.join(test_dir, check_name + "." + ext))

    # 3. 删除文档
    doc_file = os.path.normpath(os.path.join(module_path, "../../docs/clang-tidy/checks", module, check_name + ".rst"))
    remove_file(doc_file)

    # 4. CMakeLists.txt 移除 cpp
    cmake_file = os.path.join(module_path, "CMakeLists.txt")
    remove_line_from_file(cmake_file, r"\b%s\.cpp\b" % re.escape(check_name_camel))

    # 5. module 源文件移除 include 和 registerCheck
    module_cpp = get_module_filename(module_path, module)
    print(f"Module source file: {module_cpp}")
    if module_cpp:
        remove_line_from_file(module_cpp, r'#include\s*"%s\.h"' % re.escape(check_name_camel))
        remove_multiline_register_check(module_cpp, check_name_camel, module, check_name)

    # 6. ReleaseNotes.rst 移除 release note
    release_notes = os.path.normpath(os.path.join(module_path, "../../docs/ReleaseNotes.rst"))
    if os.path.isfile(release_notes):
        with io.open(release_notes, "r", encoding="utf8") as f:
            lines = f.readlines()
        with io.open(release_notes, "w", encoding="utf8", newline="\n") as f:
            skip = False
            for line in lines:
                if re.search(r":doc:`%s-%s" % (re.escape(module), re.escape(check_name)), line):
                    skip = True
                elif skip and line.strip() == "":
                    skip = False
                    continue
                if not skip:
                    f.write(line)

    # 7. 更新 checks list
    # 复用 add_new_check.py 的 update_checks_list
    try:
        from add_new_check import update_checks_list
        update_checks_list(clang_tidy_path)
    except Exception:
        pass

    print("Done.")

if __name__ == "__main__":
    main()
