#include <cstddef>

void clear_pointer(int *p)
{
    p = nullptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
}

int main()
{
    int value = 0;
    clear_pointer(&value);
    return 0;
}
