from retriever.retrieve_from_astMatchers import embedding_ast_matchers
from prompt.clang_tidy_prompt.build_prompt import get_prompt_for_clang_tidy
# if __name__ == "__main__":
    
#     for i in range(1,5):
#         print(i)
    # prompt = get_prompt_for_clang_tidy("logic_for_negative_case")
    # print(prompt)

from openai import OpenAI

client = OpenAI(
    base_url="https://api.square16.org/v1",
    api_key="sk-o1hHPSLhIHUHaynFFfMwUPsYQV86flM0a2FtxtqevCrRxkDu",
)

completion = client.chat.completions.create(
    model="deepseek-v4-flash-itkk",
    messages=[
        {"role": "user", "content": "Explain quantum entanglement in one paragraph."}
    ],
)

print(completion.choices[0].message.content)