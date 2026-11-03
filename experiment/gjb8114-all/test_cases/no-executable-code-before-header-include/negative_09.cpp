asm("nop"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]
#include <iostream>

int main() {
    std::cout << "negative_09" << std::endl;
    return 0;
}
