#include <iostream>

int main() {
    double lhs = 0.1 + 0.2;
    double rhs = 0.3;
    if (lhs == rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
        std::cout << "equal\n";
    } else {
        std::cout << "not equal\n";
    }
    return 0;
}
