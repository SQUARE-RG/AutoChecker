#include <iostream>

int main() {
    double d = 1.234567890123456;
    float f = float(d); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    std::cout << f << std::endl;
    return 0;
}
