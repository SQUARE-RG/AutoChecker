#include <cstdint>

int main() {
    std::uint32_t x = 0x80000000u;
    std::uint32_t y = x >> 33; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    (void)y;
    return 0;
}
