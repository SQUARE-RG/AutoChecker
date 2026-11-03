#include <iostream>

void report(bool value)
{
    std::cout << (value ? "true" : "false") << '\n';
}

int main()
{
    bool outReg1 = true;
    bool outReg2 = false;
    report(outReg1 < outReg2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
    return 0;
}
