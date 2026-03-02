
使用如下命令将软件克隆到本地：

```shell
git clone https://github.com/Carlson-JLQ/code_check.git
git checkout web-release
cd code_check
chmod +x scripts/install.sh
bash install.sh
cd /root/code_check/src/retriever/embedding_model
conda activate code_cehck
pip install modelscope
modelscope download --model BAAI/bge-large-en-v1.5 --local_dir /root/code_check/src/retriever/embedding_model
```