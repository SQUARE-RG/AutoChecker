#include <iostream>

int main()
{
    int i = 1;
    int product = 1;
    for (; i < 100; )
    {
        product *= 2;
        i *= 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
    }
    std::cout << product << std::endl;
    return 0;
}
