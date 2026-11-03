#include <cstdio>

#define BLOCKDEF 1U

static unsigned int fun1(void)
{
    unsigned int x = 0U;
    x = x + BLOCKDEF;
    return x;
}

#define BLOCKDEF 2U // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]

int main(void)
{
    unsigned int a1 = 0U;
    unsigned int a2 = 0U;

    a1 = fun1();
    a2 = a1 + BLOCKDEF;
    std::printf("%u\n", a2);
    return 0;
}
