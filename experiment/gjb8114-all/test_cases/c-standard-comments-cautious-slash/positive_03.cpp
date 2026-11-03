#include <iostream> /* 标准输入输出 */
#include <vector>   /* 动态数组容器 */

/* 返回两个整数的较大值 */
static int max_value(int lhs, int rhs)
{
    return lhs > rhs ? lhs : rhs;
}

int main()
{
    /* 块注释用于说明下面语句的含义 */
    int result = max_value(7, 2);
    std::cout << result << std::endl; /* 输出结果 */
    return 0;
}
