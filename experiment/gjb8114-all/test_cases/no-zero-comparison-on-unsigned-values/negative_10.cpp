#include <iostream>

int main() {
    constexpr unsigned int u = 0;
    static_assert(u >= 0, "unsigned value is not negative"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    std::cout << u << '\n';
    return 0;
}
