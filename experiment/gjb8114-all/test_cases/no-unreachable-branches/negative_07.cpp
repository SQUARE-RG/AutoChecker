#include <climits>

int adjust(int x)
{
    if (x <= INT_MAX)
    {
        return x + 1;
    }
    else
    {
        return x - 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    }
}

int main()
{
    return adjust(0);
}
