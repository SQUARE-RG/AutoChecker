#include <cstdint>

int main()
{
    std::uint64_t value = 0x8000000000000000ULL;
    std::uint64_t shifted = value >> 64; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    return 0;
}
