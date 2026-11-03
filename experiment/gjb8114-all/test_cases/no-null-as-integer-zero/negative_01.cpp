#include <cstddef>

int fun(int width);

int main()
{
    int i = fun(NULL); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
    return 0;
}

int fun(int width)
{
    int w = width - 10;
    return w;
}
