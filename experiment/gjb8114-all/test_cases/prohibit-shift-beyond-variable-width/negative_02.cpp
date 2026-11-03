#include <cstdint>

int main()
{
    std::uint64_t x = 0x8000000000000000ULL;
    std::uint64_t y = x >> 65; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    (void)y;
    return 0;
}
