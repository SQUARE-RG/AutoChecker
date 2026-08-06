from llm_interface.llm_provider import llm_client,llm_invoke

from langchain_core.prompts import PromptTemplate


code_content = ""
with open("/root/code_check/llvm-project/clang-tools-extra/clang-tidy/bugprone/SuspiciousStringCompareCheck.cpp", 'r') as f:
    code_content = f.read()

rule_des= "bugprone-suspicious-string-compare:Find suspicious usage of runtime string comparison functions.\nThis check is valid in C and C++.\n\nChecks for calls with implicit comparator and proposed to explicitly add it.\n\n.. code-block:: c++\n\n    if (strcmp(...))       // Implicitly compare to zero\n    if (!strcmp(...))      // Won't warn\n    if (strcmp(...) != 0)  // Won't warn\n\nChecks that compare function results (i.e., ``strcmp``) are compared to valid\nconstant. The resulting value is\n\n.. code::\n\n    <  0    when lower than,\n    >  0    when greater than,\n    == 0    when equals.\n\nA common mistake is to compare the result to `1` or `-1`.\n\n.. code-block:: c++\n\n    if (strcmp(...) == -1)  // Incorrect usage of the returned value.\n\nAdditionally, the check warns if the results value is implicitly cast to a\n*suspicious* non-integer type. It's happening when the returned value is used in\na wrong context.\n\n.. code-block:: c++\n\n    if (strcmp(...) < 0.)  // Incorrect usage of the returned value."

negative_test_case = ""
with open("/root/code_check/llvm-project/clang-tools-extra/test/clang-tidy/checkers/bugprone/suspicious-string-compare.cpp", 'r') as f:
    negative_test_case = f.read()

prompt = PromptTemplate(
    input_variables=["rule_description", "negative_test_case","checker_code"],
    template=""" 
    # Instruction
You are a senior Clang/LLVM expert mentoring newcomers in designing a custom Clang-Tidy checker.
Your task is to produce **step-by-step implementation logic** for the checker based on the provided **rule** , **test case code** and **checker code to reference **, including:

## **Checker Design Requirements**

A Clang-Tidy checker consists of two main parts:

### **1. AST Matcher Logic (`registerMatchers`)**

* Use the **ASTMatcher DSL** to define precise matching rules.
* Bind matched nodes with `bind("name")`.
* The matcher must reflect the checker’s rule and trigger for all relevant code patterns.

#### **2. Callback Checking Logic (`check`)**

* In `check()`, retrieve bound nodes via `Result.Nodes.getNodeAs<T>()`.
* Implement all necessary diagnostics and logic required by the rule.
* The logic here must NOT include or consider any fix-it generation or code-fix–related behavior.
* Describe each step in a clear, logical sequence.

---

# Inputs
## rule
**Rule Description:**
{rule_description}

## test case code
**Negative Test Case Code:**
{negative_test_case}

## checker code to reference
```c
{negative_test_case}
```
---

# Output Formatting Requirements

Return **only** a JSON array containing exactly one object with the following keys:

* `"logic_registerMatchers"` — an ordered list of reasoning steps describing how to design the AST matcher.
* `"logic_check"` — an ordered list of reasoning steps describing how to implement the diagnostic logic in the callback.(Reminder: no fix-it logic should appear here.)

**Do NOT:**

* include explanations, comments, or markdown
* include code fences
* add extra fields
* wrap output in text outside the JSON

## Example Output Format

```json
[
    {{
        "logic_registerMatchers": [
            "1. Match function declarations that are definitions",
            "2. Exclude function declarations with Naked attribute",
            "3. Check if a function is an override method",
            "4. bind ..."
        ],
        "logic_check": [
            "1. Get the canonical declaration of a function",
            "2. Check whether a function is a virtual method",
            "3. Check whether a function has a written prototype",
            "4. Get the number of parameters in a function"
        ]
    }}
]
```
""").format(rule_description=rule_des, negative_test_case=negative_test_case,checker_code=code_content)


response = llm_invoke(llm_client, prompt)

print(response)
# import json
# logic = json.loads(response)
# print("Logic for registerMatchers:")
# for step in logic[0]["logic_registerMatchers"]:
#     print("-", step)
# print("\nLogic for check:")
# for step in logic[0]["logic_check"]:
#     print("-", step)    