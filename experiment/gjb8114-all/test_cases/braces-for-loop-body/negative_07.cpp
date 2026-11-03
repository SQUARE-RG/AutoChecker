#include <iostream>

int main()
{
    int total = 0;
    for (int i = 0; i < 10; ++i)
        continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    std::cout << total << '\n';
    return 0;
}
