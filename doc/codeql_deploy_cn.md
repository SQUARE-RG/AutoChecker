# 安装codeql
按照如下命令安装codeql：
```shell
sudo apt update
sudo apt install build-essential libncurses-dev flex bison libssl-dev libelf-dev
# 下载codeql 
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
sudo unzip codeql-linux64.zip -d /opt/
sudo chmod -R 755 /opt/codeql

# 将 CodeQL 可执行文件路径添加到当前用户的 PATH 环境变量中
echo 'export PATH="$PATH:/opt/codeql/"' >> ~/.bashrc
source ~/.bashrc

# 验证安装
codeql version

# 获取codeSDK
cd AutoChecker
git clone https://github.com/github/codeql.git 
```