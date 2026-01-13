# 收集language_guide/cpp 的知识库

## 提取/root/code_check/codeql/docs/codeql/codeql-language-guides/目录下和cpp相关的所有文件，复制到目录/root/code_check/codeql_collect/codeql_language_guide/cpp

def collect_cpp_language_guide():
    import os
    import shutil

    source_dir = "/root/code_check/codeql/docs/codeql/codeql-language-guides/"
    target_dir = "/root/code_check/codeql_collect/codeql_language_guide/cpp"

    os.makedirs(target_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if "cpp" in file.lower():
                source_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                target_subdir = os.path.join(target_dir, relative_path)
                os.makedirs(target_subdir, exist_ok=True)
                target_file_path = os.path.join(target_subdir, file)
                shutil.copy2(source_file_path, target_file_path)
                print(f"Copied: {source_file_path} to {target_file_path}")  


## 构建RAG数据库
if __name__ == "__main__":
    collect_cpp_language_guide()