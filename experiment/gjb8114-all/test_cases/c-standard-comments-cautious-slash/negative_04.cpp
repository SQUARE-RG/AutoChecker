#include <iostream>

/* 计算并返回两数之和 */
static int add(int lhs, int rhs)
{
    return lhs + rhs;
}

int main()
{
    int sum = add(4, 6);
    // std::cout << "debug: " << sum << std::endl; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]
    std::cout << sum << std::endl;
    return 0;
}
