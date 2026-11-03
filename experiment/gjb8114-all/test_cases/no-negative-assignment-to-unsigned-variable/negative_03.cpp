#include <cstdio>

#define NEG_OFFSET (-10)

int main(void)
{
    unsigned int uCount;
    uCount = NEG_OFFSET;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    std::printf("count=%u\n", uCount);
    return 0;
}
