// 违规场景：在 #include 之前出现了可执行代码（函数定义及其函数体）。
int addTwo(int lhs, int rhs)
{
    return lhs + rhs;
}

#include <iostream> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]

int main()
{
    std::cout << addTwo(20, 22) << '\n';
    return 0;
}
