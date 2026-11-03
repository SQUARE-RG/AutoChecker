#include <cstdint>

int main()
{
    std::int32_t x = 1;
    std::int32_t y = x << 40; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-6]
    return y;
}
