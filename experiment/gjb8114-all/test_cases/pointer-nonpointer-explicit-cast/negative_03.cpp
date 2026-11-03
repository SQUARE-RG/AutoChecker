#include <cstddef>

int main()
{
    int value = 7;
    bool present = &value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
    return 0;
}
