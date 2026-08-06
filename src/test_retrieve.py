from retriever.retrieve_from_ast_api  import get_related_ast_api
from retriever.retrieve_from_check_op  import get_related_check_op
from retriever.retrieve_from_astMatchers import get_related_astMatchers
from retriever.retrieve_from_astMatchers_meta_op import  get_related_astMatchers_meta_op
from help.clang_tidy_utils import tk
logic_for_ast_api =[
    "Get the canonical declaration of a function",
    "Check whether a function is a virtual method",
    "Check whether a function has a written prototype",
    "Get the number of parameters in a function"
]

logic_for_ast_matcher=[
    "Match function declarations that are definitions",
    "Exclude function declarations with Naked attribute",
    "Check if a function is an override method",
]

def main():
    # related_ast_api = get_related_ast_api(logic_for_ast_api)

    # for i in related_ast_api:
    #     print(i)
   
    # related_check_op = get_related_check_op(logic_for_ast_api) 
    # for i in related_check_op:
    #     print(i)


    # related_ast_matchers = get_related_astMatchers(logic_for_ast_matcher)
    # for i in related_ast_matchers:
    #     print(i)


    # related_astMatchers_meta_op = get_related_astMatchers_meta_op(logic_for_ast_matcher)
    # for i in related_astMatchers_meta_op:
    #     print(i)

    astMatch_suggest_string,class_struct_suggest_string = tk(logic_for_ast_matcher,logic_for_ast_api)
    print("AST Matchers Suggestions:")
    print(astMatch_suggest_string)
    print("Class and Struct Suggestions:")
    print(class_struct_suggest_string)

if __name__ == "__main__":
    main()