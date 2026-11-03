#include <iostream>

int main()
{
    unsigned int x = 2u;
    int y = -2;
    int i;

    if (y < x) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
    {
        i = 0;
    }
    else
    {
        i = 1;
    }

    std::cout << i << std::endl;
    return 0;
}
