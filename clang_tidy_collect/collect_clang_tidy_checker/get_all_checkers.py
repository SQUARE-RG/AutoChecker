import os
import json
import re
from collections import defaultdict

def parse_rst_file(file_path):
    """解析单个 .rst 文件，提取标题、内容和代码块"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_match = re.search(r'\.\. title:: (.+)', content)
    title = title_match.group(1).strip() if title_match else "Untitled"
    
    # 提取主标题
    main_title_match = re.search(r'^([^\n]+)\n=+$', content, re.MULTILINE)
    main_title = main_title_match.group(1).strip() if main_title_match else ""
    
    # 提取描述内容（主标题之后，代码块之前）
    description = ""
    # if main_title_match:
    #     start_idx = main_title_match.end()
    #     code_start = re.search(r'\.\. code-block::', content[start_idx:])
    #     if code_start:
    #         description = content[start_idx:start_idx + code_start.start()].strip()
    #     else:
    #         description = content[start_idx:].strip()
    if main_title_match:
        description = content[main_title_match.end():].strip()

    
    # # 提取所有代码块（支持多段、空行、缩进）
    # code_blocks = []
    # # 匹配 .. code-block:: c++ 后面所有连续缩进的代码（允许空行）
    # code_block_pattern = re.compile(
    #     r'\.\. code-block:: c\+\+\s*\n((?:\n|(?:[ ]{2,}.*\n))+)', re.MULTILINE
    # )
    # for match in code_block_pattern.finditer(content):
    #     raw_code = match.group(1)
    #     # 只保留每行前面有2个及以上空格的行，去掉前导空格
    #     cleaned_lines = []
    #     for line in raw_code.splitlines():
    #         if line.strip() == "":
    #             cleaned_lines.append("")
    #         elif re.match(r'^[ ]{2,}', line):
    #             cleaned_lines.append(line.lstrip())
    #     cleaned_code = "\n".join(cleaned_lines).strip()
    #     if cleaned_code:
    #         code_blocks.append(cleaned_code)
    
    # 提取文件路径中的类别（子文件夹名称）
    category = os.path.basename(os.path.dirname(file_path))
    
    return {
        "title": title,
        "main_title": main_title,
        "description": description,
        "code_blocks": "code_blocks",
        "category": category,
        "file_path": file_path
    }

def process_checks_directory(root_dir):
    """处理整个 checks 目录"""
    results = defaultdict(list)
    
    # 遍历所有子目录和文件
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.rst') and file != "list.rst":
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                
                try:
                    file_data = parse_rst_file(file_path)
                    results[file_data["category"]].append(file_data)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    # 转换为标准字典（非 defaultdict）
    return dict(results)

def save_to_json(data, output_file):
    """将数据保存为 JSON 文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved results to {output_file}")

def main():
    # 配置路径
    checks_dir = "/root/code_check/llvm-project/clang-tools-extra/docs/clang-tidy/checks"  # 更改为您的实际路径
    output_file = "/root/code_check/clang_tidy_collect/collect_clang_tidy_checker/all_checker.json"
    
    # 处理所有文件
    all_data = process_checks_directory(checks_dir)
    
    # 添加元数据
    result = {
        "metadata": {
            "source_directory": checks_dir,
            "files_processed": sum(len(files) for files in all_data.values()),
            "categories_count": len(all_data),
            "generated_at": "2023-10-05T12:00:00Z"  # 可以替换为实际时间
        },
        "data": all_data
    }
    
    # 保存结果
    save_to_json(result, output_file)

if __name__ == "__main__":
    main()