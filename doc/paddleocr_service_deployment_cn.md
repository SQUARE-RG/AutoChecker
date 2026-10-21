# PaddleOCR CPU 部署步骤

本文档在当前 Ubuntu 22.04 CPU 服务器上部署 PaddleOCR PP-StructureV3。PaddleOCR 使用独立 Conda 环境，并以 HTTP 服务运行。

最终配置：

```text
Conda 环境：paddleocr_service
服务地址：http://127.0.0.1:18080
解析接口：POST /layout-parsing
运行设备：CPU
oneDNN：关闭（规避 Paddle 3.3.x CPU 推理兼容问题）
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

同时确认实际解释器和依赖版本，避免复用到名称相同但 Python 版本不符的旧环境：

```bash
python -c 'import sys, paddle, paddleocr, paddlex; print(sys.version); print("paddle", paddle.__version__); print("paddleocr", paddleocr.__version__); print("paddlex", paddlex.__version__)'
```

如果这里不是 Python 3.10，说明 `paddleocr_service` 环境不是按本文档新建的。需要先确认其中没有其他重要依赖，再删除并重建环境；不要仅根据环境名称判断 Python 版本。

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

PaddlePaddle 3.3.x 的 CPU oneDNN 路径在部分 PIR 模型上可能抛出以下异常：

```text
ConvertPirAttribute2RuntimeAttribute not support
[pir::ArrayAttribute<pir::DoubleAttribute>]
```

该异常发生在 Paddle 的 C++ oneDNN 推理路径，与 Python 3.10 或 3.12 没有直接关系。服务启动时设置 `PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=0`，使用普通 Paddle CPU 算子绕过该问题。这样会降低 CPU 推理速度，但不会更换 OCR 模型。

```bash
conda activate paddleocr_service

PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=0 paddlex --serve \
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

### 9.1 本地地址与 HTTP 代理

先检查当前终端是否设置了代理：

```bash
env | grep -iE '^(HTTP|HTTPS|ALL|NO)_PROXY='
```

本次排查中，执行 OCR 客户端的 Codex 命令进程被运行平台注入了以下变量：

```text
HTTP_PROXY=http://codex-proxy:2175
HTTPS_PROXY=http://codex-proxy:2175
```

这些变量不存在于容器 PID 1、`/etc/environment`、`/root/.bashrc`、`/root/.profile` 或项目 Dockerfile 中，因此不是原镜像的全局配置。不同终端继承到的环境可能不同，应当在实际启动 OCR 客户端的同一个终端中执行上述检查。

如果没有 `NO_PROXY`，Python `requests` 会把 `http://127.0.0.1:18080` 也交给该代理。短请求可能看似正常，长时间 OCR 请求则可能被代理提前断开并返回 HTTP 502。

当前终端可立即设置：

```bash
export NO_PROXY="127.0.0.1,localhost,::1"
export no_proxy="$NO_PROXY"
```

`NO_PROXY` 只让这些回环地址绕过代理，不会关闭访问外网时使用的 `HTTP_PROXY` 或 `HTTPS_PROXY`。

对于本项目构建的容器，应在 Dockerfile 中永久设置：

```dockerfile
ENV NO_PROXY="127.0.0.1,localhost,::1" \
    no_proxy="127.0.0.1,localhost,::1"
```

修改后需要重新构建并创建容器。Dockerfile 的 `ENV` 会由容器内的交互命令和后台进程共同继承，比只修改 `/root/.bashrc` 更可靠。`.bashrc` 只保证交互式 Bash 生效，直接启动的 Python 或后台服务不一定读取它。

对于暂时不能重建的现有容器，可以写入 `/etc/environment`，并在当前终端同步导出：

```bash
grep -qxF 'NO_PROXY="127.0.0.1,localhost,::1"' /etc/environment || \
  printf '%s\n' 'NO_PROXY="127.0.0.1,localhost,::1"' >> /etc/environment
grep -qxF 'no_proxy="127.0.0.1,localhost,::1"' /etc/environment || \
  printf '%s\n' 'no_proxy="127.0.0.1,localhost,::1"' >> /etc/environment

export NO_PROXY="127.0.0.1,localhost,::1"
export no_proxy="$NO_PROXY"
```

`/etc/environment` 主要供新的登录会话读取；它不能修改已经运行的进程，也不保证被 `docker exec ... <command>` 这类非登录进程读取。因此生产部署仍以 Dockerfile `ENV` 或容器启动参数 `-e NO_PROXY=... -e no_proxy=...` 为准。

### 9.2 调用接口

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

session = requests.Session()
# 此接口固定为本机回环地址，不应读取 HTTP_PROXY/HTTPS_PROXY。
session.trust_env = False

response = session.post(
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

nohup env \
  PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=0 \
  NO_PROXY="127.0.0.1,localhost,::1" \
  no_proxy="127.0.0.1,localhost,::1" \
  /root/anaconda3/envs/paddleocr_service/bin/paddlex \
  --serve \
  --pipeline /opt/autochecker-paddleocr/config/PP-StructureV3.yaml \
  --device cpu \
  --host 127.0.0.1 \
  --port 18080 \
  > /var/log/autochecker-paddleocr/service.log 2>&1 &
```

AutoChecker 的 `src/input_processing/paddle_parser.py` 会在服务地址为 `localhost`、IPv4 回环地址或 IPv6 回环地址时自动忽略环境代理。因此使用默认的 `http://127.0.0.1:18080/layout-parsing` 时，可以直接运行：

```bash
/root/anaconda3/envs/code_check/bin/python \
  scripts/parse_regulation_document.py \
  --input doc/GJB-8114-2013-mini.pdf \
  --output-dir result_input_processing/gjb8114-2013-mini
```

调用远程 PaddleOCR 地址时仍保留 `HTTP_PROXY`、`HTTPS_PROXY` 的正常行为。

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
[ ] NO_PROXY/no_proxy 包含 127.0.0.1、localhost 和 ::1
[ ] PP-StructureV3 配置生成成功
[ ] PaddleX 服务已设置 PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=0
[ ] 18080 端口未被占用
[ ] 服务首次启动并完成模型下载
[ ] PDF 接口返回结构化 JSON 和 Markdown
[ ] 后台服务日志正常
```
