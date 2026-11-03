#include <cstdlib>

int main()
{
    unsigned int value = 1U;
    unsigned int* ptr = &value;
    bool flags[2] = { false, false };
    flags[0] = ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
    return flags[0] ? 1 : 0;
}
