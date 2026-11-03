#include <iostream>

int main() {
    int signedValue = -1;
    unsigned int unsignedValue = 0u;
    int result = (signedValue > unsignedValue) ? -1 : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
    std::cout << result << std::endl;
    return 0;
}
