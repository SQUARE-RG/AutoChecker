import json
import difflib

input_path = "/root/code_check/clang_tidy_collect/collect_check_op/clang_tidy_check_op.json"
output_path = "/root/code_check/clang_tidy_collect/collect_check_op/clang_tidy_check_op_dedup.json"
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 步骤1: 按 meta_op 去重
seen_meta_op = set()
unique_meta_op = []
for item in data:
    meta_op = item.get("meta_op")
    if meta_op and meta_op not in seen_meta_op:
        seen_meta_op.add(meta_op)
        unique_meta_op.append(item)
    elif not meta_op:
        unique_meta_op.append(item)

# 步骤2: 按 meta_impl 去重
seen_meta_impl = set()
unique_meta_impl = []
for item in unique_meta_op:
    meta_impl = item.get("meta_impl")
    if meta_impl and meta_impl not in seen_meta_impl:
        seen_meta_impl.add(meta_impl)
        unique_meta_impl.append(item)
    elif not meta_impl:
        unique_meta_impl.append(item)

# 步骤3: 按 meta_impl 字段相似性去重
final_result = []
meta_impl_list = []
for item in unique_meta_impl:
    meta_impl = item.get("meta_impl")
    if not meta_impl:
        final_result.append(item)
        continue
    is_similar = False
    for exist_impl in meta_impl_list:
        if difflib.SequenceMatcher(None, meta_impl, exist_impl).ratio() >= 0.9:
            print(f"Found similar implementations:\n1: {meta_impl}\n2: {exist_impl}\n")
            is_similar = True
            break
    if not is_similar:
        meta_impl_list.append(meta_impl)
        final_result.append(item)

# 步骤4: 删除 meta_impl 以 'bind' 开头的记录
final_result = [item for item in final_result if not (item.get("meta_impl") and str(item["meta_impl"]).strip().startswith("bind"))]


with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=2, ensure_ascii=False)
