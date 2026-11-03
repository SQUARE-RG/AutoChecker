#include <cstdint>

int main() {
    std::int32_t value = 64;
    std::int32_t shift = 2;
    std::int32_t result = value >> shift; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    return result == 16 ? 0 : 1;
}
