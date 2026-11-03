#include <cstdint>

int main()
{
    std::uint64_t x = 1ull;
    x <<= 70; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    return 0;
}
