#include <cstdint>

int branch_on_unsigned(unsigned int value)
{
    if (value < 0u)
    {
        return 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    }
    else
    {
        return 0;
    }
}

int main()
{
    return branch_on_unsigned(0u);
}
