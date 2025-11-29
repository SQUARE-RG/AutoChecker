# Instruction
You are a senior Clang/LLVM expert mentoring newcomers in designing a custom Clang-Tidy checker.
Your task is to produce **step-by-step implementation logic** for the checker based on the provided **rule** and **test case code**, including:

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
    {
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
    }
]
```


```json
[
    {
        "logic_registerMatchers": [
            "1. Define a list of known string comparison functions using the provided names from KnownStringCompareFunctions and user-configurable options", 
            "2. Create a matcher for direct function calls to these string comparison functions and bind them as 'call'", 
            "3. Create a matcher for macro expansions that might contain string comparison functions (like conditionalOperator) and bind them similarly", 
            "4. Combine direct calls and macro calls into a single StringCompareCallExpr matcher using ignoringParenImpCasts", 
            "5. When WarnOnImplicitComparison is enabled, match control statements (if/while/do/for) and binary operators (&&/||) that have StringCompareCallExpr as their condition without explicit comparison operators", 
            "6. When WarnOnLogicalNotComparison is enabled, match unary '!' operators applied to StringCompareCallExpr", 
            "7. Match implicit casts of StringCompareCallExpr to non-integer types to detect suspicious type conversions", 
            "8. Match binary operators (excluding comparisons, logical, and assignment) that use StringCompareCallExpr as operands", 
            "9. Match comparison operators where StringCompareCallExpr is compared against suspicious constants (non-zero integers, characters, booleans, or negative numbers)"
        ], 
        "logic_check": [
            "1. Retrieve the bound FunctionDecl ('decl') and CallExpr ('call') nodes from the match result", 
            "2. Check if the 'missing-comparison' node exists - this indicates implicit comparison in control flow", 
            "3. Check if the 'logical-not-comparison' node exists - this indicates logical NOT operator usage", 
            "4. Check if the 'invalid-comparison' node exists - this indicates comparison with suspicious constants", 
            "5. Check if the 'suspicious-operator' node exists - this indicates usage in inappropriate binary operations", 
            "6. Check if the 'invalid-conversion' node exists - this indicates suspicious implicit casting to non-integer types", 
            "7. For each detected pattern, emit the appropriate diagnostic message with the function name and context information"
        ]
    }
]
```