#include <iostream>

int main()
{
    double a = 0.1;
    double b = 0.2;
    int i = 0;
    do
    {
        a += 0.1;
        ++i;
    } while (i < 10 && a != b); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
    std::cout << i << std::endl;
    return 0;
}
