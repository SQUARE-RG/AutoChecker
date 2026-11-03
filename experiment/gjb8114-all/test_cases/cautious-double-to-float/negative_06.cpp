#include <iostream>

int main() {
    double d1 = 1.5;
    double d2 = 2.25;
    float f = d1 + d2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    std::cout << f << std::endl;
    return 0;
}
