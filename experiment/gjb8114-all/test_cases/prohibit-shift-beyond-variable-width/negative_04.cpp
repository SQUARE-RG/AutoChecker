#include <cstdint>

int main() {
    std::uint64_t x = 1ull;
    std::uint64_t y = x << 65; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    (void)y;
    return 0;
}
