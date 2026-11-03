#include <cstdio>

#define MAX_VAL(a, b) ((a) > (b) ? (a) : (b))

static int pick(int x, int y)
{
    return MAX_VAL(x, y);
}

#define MAX_VAL(a, b) ((a) < (b) ? (b) : (a)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]

int main(void)
{
    std::printf("%d\n", pick(3, 7) + MAX_VAL(2, 5));
    return 0;
}
