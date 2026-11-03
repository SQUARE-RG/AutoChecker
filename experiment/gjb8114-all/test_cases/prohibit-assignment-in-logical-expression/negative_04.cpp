#include <iostream>

int main()
{
    int sum = 0;
    for (int i = 0; (i = i + 1) < 4; ) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
        sum += i;
    }
    std::cout << sum << std::endl;
    return 0;
}
