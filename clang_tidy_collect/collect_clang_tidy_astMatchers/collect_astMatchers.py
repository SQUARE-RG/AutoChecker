import re
import json
import html

def clean_td(text):
    # 去除所有HTML标签和实体
    text = re.sub(r'<.*?>', '', text)
    text = html.unescape(text)
    return text.strip()

def extract_node_matchers(html,pattern=r'<h2[^>]*id="decl-matchers"[^>]*>Node Matchers</h2>'):
    # 找到Node Matchers部分的<h2>
    h2_match = re.search(pattern, html)
    if not h2_match:
        return None
    start = h2_match.end()
    # 跳过后面的<p>标签，找到第一个<table>
    table_match = re.search(r'<table>(.*?)</table>', html[start:], re.DOTALL)
    if not table_match:
        return None
    table_html = table_match.group(1)

    # 匹配每个matcher的tr块
    matcher_blocks = re.findall(
        r'<tr><td>(.*?)</td><td.*?>(.*?)</td><td>(.*?)</td></tr>\s*<tr><td colspan="4" class="doc"[^>]*><pre>(.*?)</pre></td></tr>',
        table_html, re.DOTALL
    )

    matchers = []
    for ret_type, name_td, params, desc in matcher_blocks:
        name = clean_td(name_td)
        matchers.append({
            "name": name,
            "return type": clean_td(ret_type),
            "Parameters": clean_td(params),
            "description": desc.strip()
        })

    return {
        "Node Matchers": {
            "description": "Matchers for AST nodes",
            "matchers": matchers
        }
    }



def extract_narrowing_matchers(html,pattern=r'<h2[^>]*id="decl-matchers"[^>]*>Narrowing Matchers</h2>'):
    # 找到Node Matchers部分的<h2>
    h2_match = re.search(pattern, html)
    if not h2_match:
        return None
    start = h2_match.end()
    # 跳过后面的<p>标签，找到第一个<table>
    table_match = re.search(r'<table>(.*?)</table>', html[start:], re.DOTALL)
    if not table_match:
        return None
    table_html = table_match.group(1)

    # 匹配每个matcher的tr块
    matcher_blocks = re.findall(
        r'<tr><td>(.*?)</td><td.*?>(.*?)</td><td>(.*?)</td></tr>\s*<tr><td colspan="4" class="doc"[^>]*><pre>(.*?)</pre></td></tr>',
        table_html, re.DOTALL
    )

    matchers = []
    for ret_type, name_td, params, desc in matcher_blocks:
        name = clean_td(name_td)
        matchers.append({
            "name": name,
            "return type": clean_td(ret_type),
            "Parameters": clean_td(params),
            "description": desc.strip()
        })

    return {
        "Narrowing Matchers": {
            "description": "Matchers for AST nodes",
            "matchers": matchers
        }
    }


def extract_traversal_matchers(html,pattern=r'<h2[^>]*id="decl-matchers"[^>]*>AST Traversal Matchers</h2>'):
    # 找到Node Matchers部分的<h2>
    h2_match = re.search(pattern, html)
    if not h2_match:
        return None
    start = h2_match.end()
    # 跳过后面的<p>标签，找到第一个<table>
    table_match = re.search(r'<table>(.*?)</table>', html[start:], re.DOTALL)
    if not table_match:
        return None
    table_html = table_match.group(1)

    # 匹配每个matcher的tr块
    matcher_blocks = re.findall(
        r'<tr><td>(.*?)</td><td.*?>(.*?)</td><td>(.*?)</td></tr>\s*<tr><td colspan="4" class="doc"[^>]*><pre>(.*?)</pre></td></tr>',
        table_html, re.DOTALL
    )

    matchers = []
    for ret_type, name_td, params, desc in matcher_blocks:
        name = clean_td(name_td)
        matchers.append({
            "name": name,
            "return type": clean_td(ret_type),
            "Parameters": clean_td(params),
            "description": desc.strip()
        })

    return {
        "AST Traversal Matchers": {
            "description": "Matchers for AST nodes",
            "matchers": matchers
        }
    }

def main():
    html_path = "/root/code_check/llvm-project/clang/docs/LibASTMatchersReference.html"
    json_path = "/root/code_check/clang_tidy_collect/collect_clang_tidy_astMatchers/astMatchers.json"
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    node_matchers_pattern = r'<h2[^>]*id="decl-matchers"[^>]*>Node Matchers</h2>'
    node_matchers = extract_node_matchers(html_content,node_matchers_pattern)

    narrowing_Matchers_pattern = r'<h2[^>]*id="narrowing-matchers"[^>]*>Narrowing Matchers</h2>'
    narrowing_matchers = extract_narrowing_matchers(html_content,narrowing_Matchers_pattern)

    AST_Traversal_Matchers_pattern = r'<h2[^>]*id="traversal-matchers"[^>]*>AST Traversal Matchers</h2>'
    AST_traversal_matchers = extract_traversal_matchers(html_content,AST_Traversal_Matchers_pattern)
    
    ast_matchers=[]
    ast_matchers.append(node_matchers)
    ast_matchers.append(narrowing_matchers)
    ast_matchers.append(AST_traversal_matchers)
    if ast_matchers:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ast_matchers, f, indent=2, ensure_ascii=False)
        print(f"Saved AST matchers to {json_path}")
    else:
        print("No AST matchers found.")

    # if node_matchers:
    #     with open(json_path, "w", encoding="utf-8") as f:
    #         json.dump(node_matchers, f, indent=2, ensure_ascii=False)
    #     print(f"Saved node matchers to {json_path}")
    # else:
    #     print("Node Matchers section not found.")

if __name__ == "__main__":
    main()
