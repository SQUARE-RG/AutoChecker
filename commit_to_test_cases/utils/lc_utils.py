from typing import Any


def unwrap_response_text(response: Any) -> str:
    """Normalise LangChain responses to raw text."""
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        if "text" in response:
            return str(response["text"])
        if "content" in response:
            return str(response["content"])
    content = getattr(response, "content", None)
    if content is not None:
        return str(content)
    return str(response)
