#include <limits.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]

int main()
{
    int value = INT_MAX;
    return value > 0 ? 0 : 1;
}
