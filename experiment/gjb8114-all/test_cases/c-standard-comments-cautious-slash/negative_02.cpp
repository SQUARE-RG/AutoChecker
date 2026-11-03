#include <cstdint>

// This file uses a non-standard line comment. // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]
std::int32_t increment(std::int32_t value) {
    return value + 1;
}

int main() {
    return increment(41) == 42 ? 0 : 1;
}
