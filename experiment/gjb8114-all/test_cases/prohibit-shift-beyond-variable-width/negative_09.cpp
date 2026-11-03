#include <cstdint>

int main()
{
    std::uint32_t x = 0x80000000u;
    x >>= 40; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    return 0;
}
