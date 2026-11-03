#include <iostream>

int main() {
    int total = 0;
    double amount = 5.75;
    total += amount; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    std::cout << total << std::endl;
    return 0;
}
