#include <iostream>

int main() {
    double d = 3.141592653589793;
    float f = d; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    std::cout << f << std::endl;
    return 0;
}
