#include <cstddef>

static void take_ptr(int *ptr)
{
    if (ptr == NULL)
    {
        return;
    }
}

int main()
{
    take_ptr(0); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
    return 0;
}
