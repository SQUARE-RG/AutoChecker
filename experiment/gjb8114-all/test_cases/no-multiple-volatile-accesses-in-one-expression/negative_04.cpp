#include <iostream>

int combine(int a, int b)
{
    return a + b;
}

int main()
{
    volatile int flag = 3;
    int result = combine(flag, flag); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    std::cout << result << std::endl;
    return 0;
}
