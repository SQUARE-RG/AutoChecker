#include <iostream>

/* 返回两个整数之和 */
static int add(int lhs, int rhs)
{
    return lhs + rhs;
}

int main()
{
    int sum = add(3, 5);
    std::cout << sum << std::endl; // 输出计算结果 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]
    return 0;
}
