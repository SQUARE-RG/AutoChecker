#include <cstdlib>

int sub(int a, int b)
{
    return a - b;
}

int main()
{
    int (*handlers[1])(int, int) = {sub}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
    int result = handlers[0](3, 1);
    return result == 2 ? 0 : 1;
}
