#include <cstdint>
#include <iostream>

int main() {
    std::int64_t large_value = 5000000000LL; // 超出 32 位有符号整数范围
    std::int32_t narrowed = large_value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
    std::cout << narrowed << std::endl;
    return 0;
}
