#include <iostream>

int main() {
    long long total = 100;
    long long count = 3;
    long long result = total / count; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
    std::cout << result << std::endl;
    return 0;
}
