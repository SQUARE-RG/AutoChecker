#include <iostream>

double getValue()
{
    return 3.5;
}

int main()
{
    float fValue;
    fValue = getValue(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    std::cout << fValue << std::endl;
    return 0;
}
