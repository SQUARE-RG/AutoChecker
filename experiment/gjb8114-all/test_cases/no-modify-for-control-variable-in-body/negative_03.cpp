#include <iostream>

int main()
{
    int n = 10;
    for (int i = 0; i < n; ++i)
    {
        i += 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-3]
    }
    std::cout << n << std::endl;
    return 0;
}
