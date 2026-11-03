#include <iostream>

int main() {
    long long flags = 0x0F0FLL;
    long long mask = 0x00FFLL;
    long long combined = flags | mask; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    std::cout << combined << '\n';
    return 0;
}
