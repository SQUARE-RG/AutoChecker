#include <iostream>

int main() {
    int timeout = 30; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
    std::cout << timeout << std::endl;
    return 0;
}
