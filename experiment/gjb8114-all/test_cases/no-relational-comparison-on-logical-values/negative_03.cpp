#include <iostream>

bool isGreater(bool lhs, bool rhs)
{
    return lhs > rhs; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
}

int main()
{
    bool outReg1 = true;
    bool outReg2 = false;
    bool result = isGreater(outReg1, outReg2);
    std::cout << std::boolalpha << result << '\n';
    return 0;
}
