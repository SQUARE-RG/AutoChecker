#include <cstdint>

int main()
{
    unsigned int flags = 0x10u;
    unsigned int mask = 0x10u;
    unsigned int result = 0u;
    while (flags | mask == 0x10u) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-5]
    {
        result = 1u;
        break;
    }
    return static_cast<int>(result);
}
