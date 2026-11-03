#include <cstdint>
#include <iostream>

std::int16_t truncateToInt16(std::int64_t value) {
    return static_cast<std::int16_t>(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
}

int main() {
    std::int64_t value = 70000; // 超出 int16_t 范围
    std::cout << truncateToInt16(value) << std::endl;
    return 0;
}
