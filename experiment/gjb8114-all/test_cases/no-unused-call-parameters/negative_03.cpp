#include <iostream>

int main() {
    auto ignore = [](int value) { return 42; };  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
    std::cout << ignore(7) << std::endl;
    return 0;
}
