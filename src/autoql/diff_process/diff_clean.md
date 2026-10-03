过滤链条：
小 diff
  └── 基本不降噪，只转成结构化数据

大 diff
  ├── 整文件删除：二进制、测试、文档、资源、构建、非代码
  ├── 代码文件分级：main / secondary
  ├── Hunk 分类
  ├── Markdown 隐藏 import-only Hunk
  └── 其余 Hunk 截取前 3 行形成摘要

