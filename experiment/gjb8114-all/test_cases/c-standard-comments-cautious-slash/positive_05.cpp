#include <iostream>

/* 计算两个整数的和，参数含义见行内块注释 */
int compute(int a /* 第一个加数 */,
            int b /* 第二个加数 */) {
    /* 返回相加结果 */
    return a + b;
}

int main() {
    std::cout << compute(2, 3) << std::endl;
    return 0;
}
