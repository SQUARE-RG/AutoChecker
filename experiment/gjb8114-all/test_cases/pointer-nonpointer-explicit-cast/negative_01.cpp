#include <cstdint>

int main()
{
    unsigned int value = 0;
    unsigned int* ptr = &value;
    bool flag = ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
    (void)flag;
    return 0;
}
