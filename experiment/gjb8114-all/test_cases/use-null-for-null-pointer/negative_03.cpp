#include <cstddef>

int main()
{
    int value = 42;
    int *ptr = &value;
    ptr = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
    return 0;
}
