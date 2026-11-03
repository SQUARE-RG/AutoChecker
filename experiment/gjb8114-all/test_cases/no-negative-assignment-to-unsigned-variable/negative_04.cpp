#include <cstdio>

int main(void)
{
    unsigned long long ullMask;
    ullMask = -0x10;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    std::printf("mask=%llu\n", ullMask);
    return 0;
}
