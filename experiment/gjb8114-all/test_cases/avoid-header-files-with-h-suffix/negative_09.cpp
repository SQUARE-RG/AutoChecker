#include <stdint.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]

int main()
{
    uint32_t value = 42u;
    return value == 42u ? 0 : 1;
}
