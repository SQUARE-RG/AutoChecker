#include <iostream>

int main()
{
    volatile int limit = 10;
    int value = 7;
    if (value + limit > limit * 2) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    {
        std::cout << "above" << std::endl;
    }
    else
    {
        std::cout << "below" << std::endl;
    }
    return 0;
}
