#include <iostream>

int main() {
    int value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
    value = 42;
    std::cout << value << std::endl;
    return 0;
}
