#include <iostream>

int main() {
    int signedValue = -1;
    unsigned int unsignedValue = 1u;
    bool equal = (signedValue == unsignedValue); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
    std::cout << equal << std::endl;
    return 0;
}
