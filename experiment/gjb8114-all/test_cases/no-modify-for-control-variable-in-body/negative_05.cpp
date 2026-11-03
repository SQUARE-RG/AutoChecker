#include <iostream>

int main()
{
    int i;
    int sum = 0;
    for (i = 0; i < 10; ++i)
    {
        i--; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
        sum += i;
    }
    std::cout << sum << std::endl;
    return 0;
}
