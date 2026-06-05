import os
from typing import List
from entity.abstractProduct import AbstractCase
from loguru import logger
from config import global_config as config
import subprocess
from collections import OrderedDict
import re
import json

from retriever.retrieve_from_astMatchers import get_related_astMatchers
from retriever.retrieve_from_astMatchers_meta_op import get_related_astMatchers_meta_op
from retriever.retrieve_from_check_op import get_related_check_op
from retriever.retrieve_from_ast_api import get_related_ast_api
# Clang tidy check name utils
#只适用于clang tidy的checker生成过程
def get_camel_name(check_name):
    return "".join(map(lambda elem: elem.capitalize(), check_name.split("-")))


def get_camel_check_name(check_name):
    return get_camel_name(check_name) + "Check"

def count_negative_cases(Case_list: List[AbstractCase]=None):
    if Case_list is None:
        return 0
    negative_cases = [case for case in Case_list if not case.get_flag()]
    return len(negative_cases)

def select_negative_case(cases: List[AbstractCase], skipped_cases: List[AbstractCase]):
        logger.info("Selecting a negative test case...")
        
        if skipped_cases is None:
            skipped_cases = []
        logger.info(f"当前skipped list 数量：{len(skipped_cases)}")
        for case in cases:
            flag = case.get_flag()
            if not flag and case not in skipped_cases:
                return case
        return None
def parse_and_deduplicate_ast_nodes(ast_content):
    """
    解析 Clang AST 文件内容，提取所有节点并去重
    
    参数:
        ast_content: AST 文件的完整文本内容
        
    返回:
        list: 去重后的节点列表，每个节点包含类型和地址
    """
    # 使用有序字典存储节点，地址作为键，类型作为值（自动去重）
    unique_nodes = OrderedDict()
    
    # 正则表达式匹配 AST 节点
    node_pattern = re.compile(
        r'^(?P<indent>[ |`-]*)'  # 缩进部分
        r'(?P<node_type>\w+)'    # 节点类型
        r'\s+(?P<address>0x[0-9a-f]+)'  # 节点地址
    )
    
    # 逐行解析 AST
    for line in ast_content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 匹配节点行
        match = node_pattern.match(line)
        if match:
            node_type = match.group('node_type')
            address = match.group('address')
            
            # 使用地址作为唯一标识（自动去重）
            if address not in unique_nodes:
                unique_nodes[address] = node_type
    
    # 转换为节点列表格式
    # node_list = [{"type": node_type, "address": address} 
    #              for address, node_type in unique_nodes.items()]
    node_list = [node_type for node_type in unique_nodes.values() ]
    return node_list

# AST 缓存：避免对同一文件反复执行 clang -ast-dump（每次 ~1-3s）
# key = 文件绝对路径，value = (ast_txt, ast_json, ast_node_list)
_ast_cache = {}

def get_Case_AST(case_path):
    # 命中缓存 → 直接返回
    if case_path in _ast_cache:
        return _ast_cache[case_path]

    # case_code = case.get_case_code()
    # case_path = case.get_case_path()
    cmd = [config['compiler']['build_bin_clang'],
               '-Xclang','-ast-dump','-fsyntax-only' ,str(case_path)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
    if result.returncode != 0:
        logger.error(f"Error generating AST for case {case_path}: {result.stderr}")
        logger.error(f"Error runing command: {' '.join(cmd)}")
        _ast_cache[case_path] = (None, None, None)
        return None,None,None
    case_ast_txt = result.stdout
    # 按行处理并提取从 "`-" 开始的节点部分
    lines = case_ast_txt.splitlines(keepends=True)
    if not lines:
        content = ""
        case_ast_json = ""
        case_ast_node_list = []
        _ast_cache[case_path] = (content, case_ast_json, case_ast_node_list)
        return content, case_ast_json, case_ast_node_list

    found_dash_line = False
    output_lines = [lines[0]]
    for line in lines[1:]:
        if line.startswith("`-"):
            found_dash_line = True
        if found_dash_line:
            output_lines.append(line)

    # 仅保存最终清洗后的文件
    with open("./selected_case_ast_cleaned1.txt","w",encoding='utf-8') as output_file:
        output_file.writelines(output_lines)

    content = "".join(output_lines)

    case_ast_json = ''
    case_ast_node_list = parse_and_deduplicate_ast_nodes(content)
    case_ast_node_list = list(set(case_ast_node_list))  # 去重
    print("AST节点种类:", case_ast_node_list)
    print("AST节点数量:", len(case_ast_node_list))
    print("AST节点示例:", case_ast_node_list[:10])  # 打印前10个节点种类

    result_tuple = (content, case_ast_json, case_ast_node_list)
    _ast_cache[case_path] = result_tuple
    return result_tuple
# 去除编号前缀的函数
def remove_number_prefix(text):
    return re.sub(r'^\d+\.\s*', '', text)
def get_logic_json(logics_json):
    logic_for_registerMatchers=[]
    logic_for_check = []
    # import json
# logic = json.loads(response)
# print("Logic for registerMatchers:")
# for step in logic[0]["logic_registerMatchers"]:
#     print("-", step)
# print("\nLogic for check:")
# for step in logic[0]["logic_check"]:
#     print("-", step)  
    for step in logics_json[0]["logic_registerMatchers"]:
        logic_for_registerMatchers.append(remove_number_prefix(step))
    for step in logics_json[0]["logic_check"]:
        logic_for_check.append(remove_number_prefix(step))
    return logic_for_registerMatchers,logic_for_check
def get_repair_steps_string(repair_steps):
    repair_steps_string =""
    # 每个step前加一个序号
    for i, step in enumerate(repair_steps, 1):
        repair_steps_string += f"{i}. {step}\n" 
    return repair_steps_string
def get_logic_string(logics_json):
    logic_string= '**logic for registerMatchers**:\n'
    for step in logics_json[0]["logic_registerMatchers"]:
        logic_string += step + "\n"
    logic_string += "**logic for check**:\n"
    for step in logics_json[0]["logic_check"]:
        logic_string += step + "\n"
    return logic_string
# Matcher 名 → 对应 AST 节点类型的映射，用于精确过滤
_MATCHER_AST_TYPE_MAP = {
    # Node Matchers
    'functionDecl': 'FunctionDecl', 'cxxMethodDecl': 'CXXMethodDecl',
    'cxxConstructorDecl': 'CXXConstructorDecl', 'cxxDestructorDecl': 'CXXDestructorDecl',
    'recordDecl': 'RecordDecl', 'cxxRecordDecl': 'CXXRecordDecl',
    'fieldDecl': 'FieldDecl', 'varDecl': 'VarDecl', 'parmVarDecl': 'ParmVarDecl',
    'enumDecl': 'EnumDecl', 'enumConstantDecl': 'EnumConstantDecl',
    'typedefDecl': 'TypedefDecl', 'typeAliasDecl': 'TypeAliasDecl',
    'namespaceDecl': 'NamespaceDecl', 'usingDecl': 'UsingDecl',
    'functionTemplateDecl': 'FunctionTemplateDecl',
    'classTemplateDecl': 'ClassTemplateDecl',
    'callExpr': 'CallExpr', 'cxxMemberCallExpr': 'CXXMemberCallExpr',
    'cxxOperatorCallExpr': 'CXXOperatorCallExpr',
    'binaryOperator': 'BinaryOperator', 'unaryOperator': 'UnaryOperator',
    'conditionalOperator': 'ConditionalOperator',
    'ifStmt': 'IfStmt', 'forStmt': 'ForStmt', 'whileStmt': 'WhileStmt',
    'doStmt': 'DoStmt', 'switchStmt': 'SwitchStmt',
    'returnStmt': 'ReturnStmt', 'declStmt': 'DeclStmt',
    'compoundStmt': 'CompoundStmt',
    'memberExpr': 'MemberExpr', 'declRefExpr': 'DeclRefExpr',
    'integerLiteral': 'IntegerLiteral', 'stringLiteral': 'StringLiteral',
    'characterLiteral': 'CharacterLiteral', 'floatLiteral': 'FloatLiteral',
    'boolLiteral': 'CXXBoolLiteralExpr',
    'implicitCastExpr': 'ImplicitCastExpr', 'explicitCastExpr': 'ExplicitCastExpr',
    'cStyleCastExpr': 'CStyleCastExpr', 'cxxStaticCastExpr': 'CXXStaticCastExpr',
    'arraySubscriptExpr': 'ArraySubscriptExpr',
    'parenExpr': 'ParenExpr', 'parenListExpr': 'ParenListExpr',
    'initListExpr': 'InitListExpr',
    # Narrowing Matchers
    'hasName': None, 'hasType': None, 'isDefinition': None,
    'isConst': None, 'isStatic': None, 'isVolatile': None,
    'isPublic': None, 'isPrivate': None, 'isProtected': None,
    'isVirtual': None, 'isOverride': None, 'isFinal': None,
    'isDeleted': None, 'isDefaulted': None, 'isExplicit': None,
    'isNoThrow': None, 'isConstexpr': None,
    'isAnonymous': 'NamespaceDecl',  # 注意：这个是匿名命名空间，不是匿名结构体！
    'isAnonymousStructOrUnion': 'RecordDecl',  # 这才是匿名结构体/联合体
    # Traversal Matchers (通用，不过滤)
    'has': None, 'hasDescendant': None, 'hasAncestor': None,
    'hasParent': None, 'forEach': None, 'forEachDescendant': None,
    'allOf': None, 'anyOf': None, 'anything': None, 'unless': None,
    'optionally': None, 'ignoringParenImpCasts': None,
    'ignoringImplicit': None, 'ignoringElidableConstructors': None,
    'to': None, 'hasDeclaration': None, 'pointsTo': None,
    'references': None, 'isDerivedFrom': None, 'isSameOrDerivedFrom': None,
}

_GENERIC_MATCHERS = {
    'allOf', 'anyOf', 'anything', 'unless', 'optionally',
    'has', 'hasDescendant', 'hasAncestor', 'hasParent',
    'forEach', 'forEachDescendant', 'to', 'hasDeclaration',
    'ignoringParenImpCasts', 'ignoringImplicit',
}

def _score_doc_ast_relevance(doc: str, ast_node_types: list) -> float:
    """计算文档与当前测试用例 AST 的相关度分数。

    策略：
    1. 文档中提到的 AST 节点类型越多 → 分数越高
    2. 如果 matcher 对应一个具体的 AST 类型，且该类型不在测试用例中 → 可能是噪音
    3. 通用 traversal matcher（allOf, has, unless...）→ 给基础分，不过滤
    """
    score = 0.0
    doc_lower = doc.lower()

    for ast_type in ast_node_types:
        # 精确匹配 AST 类型名
        if ast_type.lower() in doc_lower:
            score += 1.0
        # 去掉 CXX 前缀再匹配（CXXRecordDecl → RecordDecl）
        elif ast_type.startswith('CXX') and ast_type[3:].lower() in doc_lower:
            score += 0.8

    # 通用 matcher 给基础分，防止被完全过滤
    for gm in _GENERIC_MATCHERS:
        if gm.lower() in doc_lower:
            score += 0.3
            break  # 只加一次

    return score


def filter_by_ast_relevance(documents: list, ast_node_types: list,
                            top_k: int = 3) -> list:
    """用 AST 节点类型后过滤检索结果。

    输入：retriever 返回的文档列表 + 测试用例的 AST 节点类型列表
    输出：按 AST 相关度重排后的 top_k 文档

    如果所有文档相关度都为 0（没匹配到任何 AST 类型），回退到原始 top_k。
    """
    if not ast_node_types or not documents:
        return documents[:top_k]

    if len(documents) <= top_k:
        return documents

    scored = [(doc, _score_doc_ast_relevance(doc, ast_node_types))
              for doc in documents]
    scored.sort(key=lambda x: x[1], reverse=True)

    # 如果最高分也是 0，说明 AST 过滤没命中，回退
    if scored[0][1] == 0:
        return documents[:top_k]

    # 取分数 > 0 的，不够 top_k 就用原始顺序补齐
    filtered = [doc for doc, s in scored if s > 0]
    if len(filtered) < top_k:
        for doc, s in scored:
            if doc not in filtered:
                filtered.append(doc)
            if len(filtered) >= top_k:
                break

    return filtered[:top_k]


def get_most_similar_astMatcher_and_class_struct(node:list, logics_json):
    astMatch_suggest_string = ''
    class_struct_suggest_string = ''
    logic_for_registerMatchers, logic_for_check = get_logic_json(logics_json)

    # node 是测试用例的 AST 节点类型列表，用于过滤不相关的 API
    ast_node_types = node if node else []

    # astMatchers: 检索 + AST 过滤
    related_astMatchers = get_related_astMatchers(logic_for_registerMatchers)
    if ast_node_types:
        related_astMatchers = filter_by_ast_relevance(related_astMatchers, ast_node_types, top_k=3)
    for a in related_astMatchers:
        astMatch_suggest_string += a + "\n"

    # astMatchers meta op: 检索 + AST 过滤
    related_astMatchers_meta_op = get_related_astMatchers_meta_op(logic_for_registerMatchers)
    if ast_node_types:
        related_astMatchers_meta_op = filter_by_ast_relevance(related_astMatchers_meta_op, ast_node_types, top_k=3)
    for b in related_astMatchers_meta_op:
        astMatch_suggest_string += b + "\n"

    # check op: 检索 + AST 过滤
    related_check_op = get_related_check_op(logic_for_check)
    if ast_node_types:
        related_check_op = filter_by_ast_relevance(related_check_op, ast_node_types, top_k=3)
    for c in related_check_op:
        class_struct_suggest_string += c + "\n"

    # ast api: 检索 + AST 过滤
    related_ast_api = get_related_ast_api(logic_for_check)
    if ast_node_types:
        related_ast_api = filter_by_ast_relevance(related_ast_api, ast_node_types, top_k=3)
    for d in related_ast_api:
        class_struct_suggest_string += d + "\n"

    return astMatch_suggest_string, class_struct_suggest_string

def _extract_ast_types_from_code(snippets: list) -> list:
    """从代码片段中提取 AST 节点类型名称。

    代码片段中通常包含如 Result.Nodes.getNodeAs<RecordDecl>("x")、
    const auto *Struct = ...、FieldDecl::isAnonymousStructOrUnion() 等模式。
    """
    # AST 节点类型通常以 Decl/Stmt/Expr/Type/Literal/Attr/Specifier 结尾
    # 注意：cxxRecordDecl、cxxMethodDecl 等以小写开头
    ast_type_pattern = re.compile(
        r'\b([a-zA-Z][a-zA-Z0-9]*('
        r'Decl|Stmt|Expr|Type|Literal|Attr|Specifier'
        r'))\b'
    )
    types = set()
    for snippet in snippets:
        for m in ast_type_pattern.finditer(snippet):
            types.add(m.group(1))
    return list(types)


def get_suggest_string_from_hint(hint):
    result = ''
    # 从 hint 代码片段中提取 AST 类型名用于过滤
    ast_types = _extract_ast_types_from_code(hint) if hint else []

    related_astMatchers = get_related_astMatchers(hint)
    if ast_types:
        related_astMatchers = filter_by_ast_relevance(related_astMatchers, ast_types, top_k=3)
    for a in related_astMatchers:
        result += a + "\n"

    related_astMatchers_meta_op = get_related_astMatchers_meta_op(hint)
    if ast_types:
        related_astMatchers_meta_op = filter_by_ast_relevance(related_astMatchers_meta_op, ast_types, top_k=3)
    for b in related_astMatchers_meta_op:
        result += b + "\n"

    related_check_op = get_related_check_op(hint)
    if ast_types:
        related_check_op = filter_by_ast_relevance(related_check_op, ast_types, top_k=3)
    for c in related_check_op:
        result += c + "\n"

    related_ast_api = get_related_ast_api(hint)
    if ast_types:
        related_ast_api = filter_by_ast_relevance(related_ast_api, ast_types, top_k=3)
    for d in related_ast_api:
        result += d + "\n"
    return result
# def tk(logic_for_registerMatchers,logic_for_check):
#     astMatch_suggest_string= '' 
#     class_struct_suggest_string = ''
#     related_astMatchers= get_related_astMatchers(logic_for_registerMatchers)
#     logger.info(f"相关的AST Matchers建议:\n{related_astMatchers}")
#     related_astMatchers_meta_op= get_related_astMatchers_meta_op(logic_for_registerMatchers)
#     logger.info(f"相关的AST Matchers Meta Op建议:\n{related_astMatchers_meta_op}")
#     for a in related_astMatchers:
#         astMatch_suggest_string += a + "\n"
#     for b in related_astMatchers_meta_op:
#         astMatch_suggest_string += b + "\n"


#     related_check_op= get_related_check_op(logic_for_check)
#     logger.info(f"相关的Check Op建议:\n{related_check_op}")
#     for c in related_check_op:
#         class_struct_suggest_string += c + "\n" 
#     related_ast_api= get_related_ast_api(logic_for_check)
#     logger.info(f"相关的AST API建议:\n{related_ast_api}")
#     for d in related_ast_api:
#         class_struct_suggest_string += d + "\n" 
#     return astMatch_suggest_string,class_struct_suggest_string


# def parse_cpp_h_code_from_answer(answer: str):
#     """返回第一个 ```cpp ... ``` 中的纯代码，若无则 None。"""
#     # 定义正则表达式模式
#     cpp_pattern = r"checker_cpp:\s*```cpp\s*(.*?)\s*```"
#     h_pattern = r"checker_h:\s*```cpp\s*(.*?)\s*```"
#     # 使用 re.DOTALL 使 . 匹配包括换行符在内的所有字符
#     cpp_match = re.search(cpp_pattern, answer, re.DOTALL)
#     h_match = re.search(h_pattern, answer, re.DOTALL)
    
#     # 提取代码内容
#     checker_cpp_code = cpp_match.group(1).strip() if cpp_match else None
#     checker_h_code = h_match.group(1).strip() if h_match else None
#     return checker_cpp_code,checker_h_code


# ...existing code...
def parse_cpp_h_code_from_answer(answer: str):
    """
    更鲁棒的解析：优先按标签匹配 `checker_cpp:` / `checker_h:` 后的 ```cpp``` 代码块；
    若未命中则退化为取回答中出现的前两个 ```cpp``` 代码块作为 cpp 和 h。
    """
    # 优先按带标签的 code fence 提取（支持 cpp 或 c++）
    cpp_pattern = r"checker_cpp\s*:\s*```(?:cpp|c\+\+)\s*(.*?)\s*```"
    h_pattern = r"checker_h\s*:\s*```(?:cpp|c\+\+)\s*(.*?)\s*```"
    cpp_match = re.search(cpp_pattern, answer, re.IGNORECASE | re.DOTALL)
    h_match = re.search(h_pattern, answer, re.IGNORECASE | re.DOTALL)

    checker_cpp_code = cpp_match.group(1).strip() if cpp_match else None
    checker_h_code = h_match.group(1).strip() if h_match else None

    # 回退：如果没有按标签找到，尝试抓取所有 ```cpp``` code block，并用前两个作为 cpp/h
    if not checker_cpp_code or not checker_h_code:
        blocks = re.findall(r"```(?:cpp|c\+\+)\s*(.*?)\s*```", answer, re.IGNORECASE | re.DOTALL)
        if blocks:
            if not checker_cpp_code and len(blocks) >= 1:
                checker_cpp_code = blocks[0].strip()
            if not checker_h_code and len(blocks) >= 2:
                checker_h_code = blocks[1].strip()

    return checker_cpp_code, checker_h_code
# ...existing code...

def save_checker_code(checker_cpp: str, checker_h:str,rule_name: str):
    """将生成的检查器代码保存到指定路径。"""
    ruler_checker_cpp = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".cpp"
    with open(ruler_checker_cpp, 'w', encoding='utf-8') as file:
        file.write(checker_cpp)
    ruler_checker_h = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".h"
    with open(ruler_checker_h, 'w', encoding='utf-8') as file:
        file.write(checker_h)
    return ""

def get_checker_code(rule_name: str):

    """读取指定规则名称的检查器代码。"""
    ruler_checker_cpp = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".cpp"    
    with open(ruler_checker_cpp, 'r', encoding='utf-8') as file:
        checker_code = file.read()
    ruler_checker_h = config['checker']['checker_path'] + get_camel_check_name(rule_name) + ".h"
    with open(ruler_checker_h, 'r', encoding='utf-8') as file:
        checker_h = file.read()
    return checker_code,checker_h

def save_middle_check(checker_cpp: str, checker_h:str,round_dir: str):
    """将生成的中间检查器代码保存到指定路径。"""
    ruler_checker_cpp = os.path.join(round_dir, "checker.cpp")
    with open(ruler_checker_cpp, 'w', encoding='utf-8') as file:
        file.write(checker_cpp)
    ruler_checker_h = os.path.join(round_dir, "checker.h")
    with open(ruler_checker_h, 'w', encoding='utf-8') as file:
        file.write(checker_h)
    return ""