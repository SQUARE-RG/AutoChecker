#include <cstdio>

#define NEGATE(x) (-x)  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-7]

int main()
{
    int a = 5;
    int b = 3;
    int r = NEGATE(a + b);
    std::printf("%d\n", r);
    return 0;
}
