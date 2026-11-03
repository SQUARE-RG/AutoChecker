#include <iostream>

int main() {
    double value = 2.5;
    int result = static_cast<int>(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    std::cout << result << '\n';
    return 0;
}
