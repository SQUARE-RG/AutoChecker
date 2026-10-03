# PaddleOCR CPU 部署步骤

本文档在当前 Ubuntu 22.04 CPU 服务器上部署 PaddleOCR PP-StructureV3。PaddleOCR 使用独立 Conda 环境，并以 HTTP 服务运行。

最终配置：

```text
Conda 环境：paddleocr_service
服务地址：http://127.0.0.1:18080
解析接口：POST /layout-parsing
运行设备：CPU
```

以下命令均在服务器上手动执行。

## 1. 安装系统依赖

```bash
apt-get update
apt-get install -y libgl1 libglib2.0-0 libgomp1
```

确认 Conda 可用：

```bash
conda --version
```

## 2. 创建独立 Conda 环境

```bash
conda create -n paddleocr_service python=3.10 
```

如果出现 Anaconda Terms of Service 未接受的错误，先执行：

```bash
conda tos accept --override-channels \
  --channel https://repo.anaconda.com/pkgs/main

conda tos accept --override-channels \
  --channel https://repo.anaconda.com/pkgs/r
```

然后重新运行 `conda create`。

激活环境：

```bash
conda activate paddleocr_service
python --version
which python
```

预期结果：

```text
Python 3.10.x
/root/anaconda3/envs/paddleocr_service/bin/python
```

Conda 会自动把命名环境放到自己的 `envs` 目录。当前服务器的 Conda 位于 `/root/anaconda3`，因此不需要手动在 `/opt` 下创建环境目录。

后续安装命令都必须在这个环境中执行。

## 3. 安装 PaddlePaddle CPU 版

```bash
python -m pip install --upgrade pip setuptools wheel

python -m pip install paddlepaddle==3.3.0 \
  -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```

验证：

```bash
python -c "import paddle; print(paddle.__version__); paddle.utils.run_check()"
```

预期包含：

```text
3.3.0
PaddlePaddle is installed successfully!
```

## 4. 安装 PaddleOCR

安装 PaddleOCR 和 PP-StructureV3 文档解析依赖：

```bash
python -m pip install "paddleocr[doc-parser]==3.7.0"
```

验证：

```bash
python -c "import paddleocr; print(paddleocr.__version__)"
paddleocr --help
paddlex --help
```

预期 PaddleOCR 版本为 `3.7.0`。

## 5. 安装 HTTP Serving

```bash
paddlex --install serving
paddlex --serve --help
```

保存依赖版本：

```bash
mkdir -p /opt/autochecker-paddleocr
python -m pip freeze \
  > /opt/autochecker-paddleocr/requirements.lock.txt
```

## 6. 获取 PP-StructureV3 配置

```bash
mkdir -p /opt/autochecker-paddleocr/config

paddlex --get_pipeline_config PP-StructureV3 \
  --save_path /opt/autochecker-paddleocr/config

ls -l /opt/autochecker-paddleocr/config
```

预期存在：

```text
/opt/autochecker-paddleocr/config/PP-StructureV3.yaml
```

编辑该 YAML，在顶层添加：

```yaml
Serving:
  visualize: false
  extra:
    max_num_input_imgs: 30
```

该配置关闭图片返回，并限制单次最多处理 30 页。长 PDF 建议在调用前切分成不超过 20 页的子 PDF。

## 7. 检查服务端口

本方案使用 `18080`。启动前检查端口：

```bash
python - <<'PY'
import socket

sock = socket.socket()
try:
    sock.bind(("127.0.0.1", 18080))
    print("port 18080 is available")
finally:
    sock.close()
PY
```

如果出现 `Address already in use`，把后续命令中的 `18080` 换成其他未占用端口。

## 8. 启动 PaddleOCR HTTP 服务

```bash
conda activate paddleocr_service

paddlex --serve \
  --pipeline /opt/autochecker-paddleocr/config/PP-StructureV3.yaml \
  --device cpu \
  --host 127.0.0.1 \
  --port 18080
```

首次启动会自动下载 PP-StructureV3 模型，需要等待下载完成。成功后应看到：

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:18080
```

保持当前终端运行，打开另一个终端测试接口。

## 9. 测试解析接口

在另一个终端执行：

```bash
conda activate paddleocr_service
python -m pip install requests
```

创建 `test_paddleocr.py`：

```python
import base64
import json
from pathlib import Path

import requests

input_file = Path("/path/to/test.pdf")
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
```

把 `/path/to/test.pdf` 修改成实际 PDF 路径，然后运行：

```bash
python test_paddleocr.py
```

成功后生成 `paddleocr_response.json`。其中：

- `result.layoutParsingResults` 是逐页结果；
- `prunedResult` 是结构化 JSON；
- `markdown.text` 是该页 Markdown。

图片输入时，把 `fileType` 改成 `1`。

## 10. 后台运行

接口测试成功后，先停止前台服务，然后执行：

```bash
mkdir -p /var/log/autochecker-paddleocr

nohup /root/anaconda3/envs/paddleocr_service/bin/paddlex \
  --serve \
  --pipeline /opt/autochecker-paddleocr/config/PP-StructureV3.yaml \
  --device cpu \
  --host 127.0.0.1 \
  --port 18080 \
  > /var/log/autochecker-paddleocr/service.log 2>&1 &
```

查询进程：

```bash
ps -ef | grep '[p]addlex.*18080'
```

查看日志：

```bash
tail -f /var/log/autochecker-paddleocr/service.log
```

停止服务时先查询准确 PID，然后执行：

```bash
kill <PID>
```

## 11. AutoChecker 调用地址

```text
POST http://127.0.0.1:18080/layout-parsing
```

建议配置：

```json
{
  "paddleocr": {
    "base_url": "http://127.0.0.1:18080",
    "layout_endpoint": "/layout-parsing",
    "connect_timeout_seconds": 30,
    "read_timeout_seconds": 7200,
    "max_pages_per_request": 20
  }
}
```

## 12. 部署检查

```text
[ ] 独立 Conda 环境创建成功
[ ] Python 版本为 3.10
[ ] PaddlePaddle 3.3.0 检查通过
[ ] PaddleOCR 3.7.0 安装成功
[ ] PaddleX Serving 安装成功
[ ] PP-StructureV3 配置生成成功
[ ] 18080 端口未被占用
[ ] 服务首次启动并完成模型下载
[ ] PDF 接口返回结构化 JSON 和 Markdown
[ ] 后台服务日志正常
```
