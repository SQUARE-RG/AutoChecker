#include <cstdlib>

int fun(int para1, int para2);

int main()
{
    int a = 2, b = 1, c = 0;
    int (*p)(int, int) = fun; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
    c = p(a, b);
    (void)c;
    return 0;
}

int fun(int para1, int para2)
{
    return para1 - para2;
}
