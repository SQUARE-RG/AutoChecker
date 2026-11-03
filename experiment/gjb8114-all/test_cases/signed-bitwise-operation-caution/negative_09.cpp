#include <iostream>

int main() {
    long flags = 1L;
    flags <<= 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    std::cout << flags << std::endl;
    return 0;
}
