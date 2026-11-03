#include <cmath>
#include <iostream>

int main() {
    double input = -7.5;
    float magnitude = std::abs(input); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    std::cout << magnitude << std::endl;
    return 0;
}
