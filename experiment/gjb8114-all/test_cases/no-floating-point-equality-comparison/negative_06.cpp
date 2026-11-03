#include <iostream>

bool different(double a, double b) {
    return a != b; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
}

int main() {
    std::cout << std::boolalpha << different(0.1, 0.2) << '\n';
    return 0;
}
