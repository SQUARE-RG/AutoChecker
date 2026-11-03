#include <iostream>

int main() {
    float value = 1.5f;
    double delta = 2.25;
    value += delta; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-2]
    std::cout << value << std::endl;
    return 0;
}
