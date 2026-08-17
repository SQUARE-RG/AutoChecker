"""从 agent 文本回答中提取 CodeQL query 代码。

严格锚点解析：只认 `query_code:` 后跟 ```query/```ql 围栏块。
不做任何宽松 fallback（任意代码块、结构定位）——检索文档里的
```codeql 示例块绝不能被误提取。
"""

import re

_ANCHOR = re.compile(
    r"query_code\s*:\s*```(?:query|ql)\s*\n?(.*?)```",
    re.IGNORECASE | re.DOTALL,
)


def find_query_code_block(answer: str) -> str | None:
    """在文本中找第一个 query_code: ```query 锚点块，返回块内容（未 strip）。

    找不到锚点 → None。注意：只找锚点，不管块内容质量
    （质量校验由调用方做：碎片/污染判定需要原始块内容）。
    """
    if not answer:
        return None
    m = _ANCHOR.search(answer)
    if m:
        return m.group(1)
    return None
