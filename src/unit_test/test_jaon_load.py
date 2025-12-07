
import json
import re


answer ="""
[
    {
        "repair_step": [
            "Identify the incorrect API usage: The code uses `DeclarationName::isOverloadedOperator()` and `DeclarationName::getOverloadedOperator()`, which are not valid member functions in the LLVM/Clang API.",
            "Check the correct API: The proper way to determine if a `DeclarationName` represents an overloaded operator is to use `DeclarationName::getNameKind()` and compare it to `DeclarationName::CXXOperatorName`. To get the operator kind, use `DeclarationName::getCXXOverloadedOperator()`.",
            "Replace the erroneous calls: Change `Name.isOverloadedOperator()` to `Name.getNameKind() == DeclarationName::CXXOperatorName`. Change `Name.getOverloadedOperator()` to `Name.getCXXOverloadedOperator()`.",
            "Update the variable type if needed: The variable `Op` is already of type `OverloadedOperatorKind`, which is the return type of `getCXXOverloadedOperator()`, so no change is required there."
        ]
    },
    {
        "wait_retrieve_code_snippet": [
            "DeclarationName::isOverloadedOperator()",
            "DeclarationName::getOverloadedOperator()",
            "DeclarationName::getNameKind()",
            "DeclarationName::CXXOperatorName",
            "DeclarationName::getCXXOverloadedOperator()"
        ]
    }
]
"""
cleaned = re.sub(r'```json|```', '', answer).strip()
print("Cleaned answer:")
print(cleaned)
try:
    data = json.loads(cleaned)
except json.JSONDecodeError as e:
    print(f"JSON decoding failed: {e}")

