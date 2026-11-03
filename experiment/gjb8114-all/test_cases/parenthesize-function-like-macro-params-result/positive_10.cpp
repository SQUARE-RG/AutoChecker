#include <cstdio>

#define NEGATE(x) (-(x))

int main()
{
    int a = 5;
    int b = 3;
    int r = NEGATE(a + b);
    std::printf("%d\n", r);
    return 0;
}
