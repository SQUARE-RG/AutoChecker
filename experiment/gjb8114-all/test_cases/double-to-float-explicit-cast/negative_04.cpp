#include <iostream>

int main()
{
    double dValues[3] = {1.25, 2.5, 3.75};
    float fValue;
    fValue = dValues[1]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    std::cout << fValue << std::endl;
    return 0;
}
