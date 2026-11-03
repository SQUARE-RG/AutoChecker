#include <cstdint>

int main()
{
    std::uint64_t x = 0xFFFFFFFFFFFFFFFFULL;
    x >>= 70; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    return static_cast<int>(x);
}
