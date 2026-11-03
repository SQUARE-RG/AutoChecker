#include <array>
#include <iostream>

int main() {
    std::array<char, 4> values{};  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
    values[0] = 1;
    values[1] = 2;
    int sum = values[0] + values[1];
    std::cout << sum << '\n';
    return 0;
}
