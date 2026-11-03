#include <cstddef>

int main()
{
    int value;
    value = NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
    return value;
}
