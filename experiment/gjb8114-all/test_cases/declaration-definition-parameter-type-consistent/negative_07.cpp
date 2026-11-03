#include <iostream>

int compute(signed int value);

int main()
{
    signed int v = 5;
    std::cout << compute(v) << std::endl;
    return 0;
}

int compute(unsigned int value) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    return static_cast<int>(value) + 1;
}
