#include <cstdlib>

int fun(int value);
int apply(int (*fp)(int), int value);

int main()
{
    return apply(fun, 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
}

int apply(int (*fp)(int), int value)
{
    return fp(value);
}

int fun(int value)
{
    return value + 1;
}
