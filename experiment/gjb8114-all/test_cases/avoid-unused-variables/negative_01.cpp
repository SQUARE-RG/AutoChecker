#include <iostream>
int main() {
    int unused_value = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
    std::cout << 0 << std::endl;
    return 0;
}
