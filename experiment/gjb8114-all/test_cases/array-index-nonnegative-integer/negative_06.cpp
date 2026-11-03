#include <climits>

int main(void)
{
    int Data[3] = {0, 0, 0};
    Data[INT_MIN] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
    return 0;
}
