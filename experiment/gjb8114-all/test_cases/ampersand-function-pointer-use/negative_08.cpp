#include <cstdlib>

int sub(int a, int b)
{
    return a - b;
}

struct Operation
{
    int (*func)(int, int);
};

int main()
{
    Operation op = {sub}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
    int result = op.func(3, 1);
    return result == 2 ? 0 : 1;
}
