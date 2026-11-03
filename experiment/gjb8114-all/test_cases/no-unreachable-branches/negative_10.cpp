#include <cstddef>

int branch_on_sizeof()
{
    if (sizeof(int) > 0u)
    {
        return 1;
    }
    else
    {
        return 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    }
}

int main()
{
    return branch_on_sizeof();
}
