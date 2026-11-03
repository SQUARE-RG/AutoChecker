#include <iostream>

int main() {
    int sum = 0;
    for (int i = 0; i < 10; ++i)
        sum += i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    std::cout << sum << std::endl;
    return 0;
}
