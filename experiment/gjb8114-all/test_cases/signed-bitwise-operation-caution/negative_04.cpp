#include <cstdint>

int main() {
    std::int32_t flags = 0x0F;
    std::int32_t mask = 0x03;
    std::int32_t result = flags ^ mask; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    return result == 0x0C ? 0 : 1;
}
