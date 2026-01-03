# Stage-1 多 Agent 测试用例提取

## 输入
- Patch 描述：`patch.md`
- 修复前代码：`before/drivers/spi/spi-pci1xxxx.c`
- 修复后代码：`after/drivers/spi/spi-pci1xxxx.c`

## Agent 职责
- **主 Agent**：解析 patch，抽象漏洞 pattern（"devm_kzalloc 分配结果未判空即解引用"），并裁剪修复前/后的代码，仅保留循环中的分配与关键字段。
- **搜索 Agent**：根据原文件头文件需求补齐 `devm_kzalloc()`、`devm_spi_alloc_host()` 等外部符号的最小可编译假实现，并移除与漏洞无关的内核依赖。
- **验证 Agent**：使用 `gcc -std=c11` 对生成的 before/after 测试用例进行编译校验，保证切片可独立编译；如失败则回传给主 Agent 调整。当前轮均已一次编译通过。

## 漏洞 Pattern
`devm_kzalloc()` 返回值未检查，在失败时立即被 `spi_bus->spi_int[iter]` 解引用，导致空指针解引用。修复方法是在解引用前返回 `-ENOMEM`。

## 生成的测试用例
- 漏洞版：`stage1/buggy_case/pci1xxxx_spi_bug.c`（含 `// CHECK-MESSAGES:` 标注）
- 修复版：`stage1/fixed_case/pci1xxxx_spi_fix.c`

两份代码均只保留 `pci1xxxx_spi_probe()` 所需的结构与 stub，实现了最小复现场景：
1. 循环中的 `devm_kzalloc()` 分配（漏洞点）；
2. `devm_spi_alloc_host()` 依赖通过假实现满足编译；
3. 其他硬件流程（IRQ、DMA、寄存器）全部删除。

## 构建记录
```
cd /root/code_check/commit_to_test_cases/linux_kernel_test_cases/1f886a7bfb3faf4c1021e73f045538008ce7634e-Null-Pointer-Dereference/stage1/buggy_case && gcc -std=c11 -Wall -Wextra -pedantic -o pci_bug pci1xxxx_spi_bug.c

cd /root/code_check/commit_to_test_cases/linux_kernel_test_cases/1f886a7bfb3faf4c1021e73f045538008ce7634e-Null-Pointer-Dereference/stage1/fixed_case && gcc -std=c11 -Wall -Wextra -pedantic -o pci_fix pci1xxxx_spi_fix.c


```

## 下一步
阶段一（提取 + 可编译验证）已完成。后续阶段可在 `test_case_result/` 中沉淀最终测试用例，并将同类 pattern 泛化到其它补丁。