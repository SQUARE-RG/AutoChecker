提取codeql所有合法的import语句
递归遍历/root/code_check/codeql/cpp/ql/lib/semmle/code/cpp目录下及其子目录下的所有.qll文件，提取文件名称和相对路径
例如/root/code_check/codeql/cpp/ql/lib/semmle/code/cpp/controlflow/ControlFlowGraph.qll 提取相对路径为semmle/code/cpp/controlflow/ControlFlowGraph.qll
则将其转换成import语句为import semmle.code.cpp.controlflow.ControlFlowGraph
将所有提取的import语句保存到一个文本文件中，每行一个import语句，文件命名为codeql_imports.txt
子文件夹排除名字叫internal的文件夹
例如/root/code_check/codeql/cpp/ql/lib/semmle/code/cpp/controlflow/BasicBlocks.qll import语句为import semmle.code.cpp.controlflow.BasicBlocks
例如/root/code_check/codeql/cpp/ql/lib/semmle/code/cpp/Function.qll import语句为import semmle.code.cpp.Function