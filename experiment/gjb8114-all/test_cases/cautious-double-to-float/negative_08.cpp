#include <iostream>

int main() {
    bool choose = true;
    double d = 2.718281828459045;
    float f = choose ? d : 0.0f; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    std::cout << f << std::endl;
    return 0;
}
