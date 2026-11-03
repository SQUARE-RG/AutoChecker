#include <cstdlib>

int adjust(int a, int *b);

int main(void)
{
    int i = 1;
    int j = 2;
    int k = adjust(i, &j);
    return k - 1;
}

int adjust(int a, int *b)
{
    if (1 == a)
    {
        *b = *b + a;
        return 1;
    }
    else
    {
        *b = *b - a;
    }
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]
