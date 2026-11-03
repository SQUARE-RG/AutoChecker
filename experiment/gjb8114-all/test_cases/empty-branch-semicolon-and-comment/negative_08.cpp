#include <iostream>

int main()
{
    int value = 3;
    int result = 0;
    if (value > 0)
    {
        result = value * 2;
    }
    else
    {
        ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]
        /* no deal with */
    }
    std::cout << result << std::endl;
    return 0;
}
