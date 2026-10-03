import base64
import json
from pathlib import Path

import requests

input_file = Path("doc/GJB-8114-2013-mini.pdf")
output_file = Path("./paddleocr_response.json")

payload = {
    "file": base64.b64encode(input_file.read_bytes()).decode("ascii"),
    "fileType": 0,
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useTextlineOrientation": False,
    "useSealRecognition": False,
    "useTableRecognition": True,
    "useFormulaRecognition": False,
    "useChartRecognition": False,
    "formatBlockContent": True,
    "returnMarkdownImages": False,
    "visualize": False,
}

response = requests.post(
    "http://127.0.0.1:18080/layout-parsing",
    json=payload,
    timeout=(30, 7200),
)
response.raise_for_status()

result = response.json()
output_file.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

pages = result["result"]["layoutParsingResults"]
print(f"parsed pages: {len(pages)}")
print(f"result: {output_file.resolve()}")