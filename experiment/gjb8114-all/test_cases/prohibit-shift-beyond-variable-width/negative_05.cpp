#include <cstdint>

int main()
{
    std::uint32_t value = 1u;
    std::uint32_t shifted = value << 32; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    return 0;
}
