#include <iostream>

int main()
{
    double a = 0.1 + 0.2;
    double b = 0.3;
    bool equal = (a == b) ? true : false; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
    std::cout << equal << std::endl;
    return 0;
}
