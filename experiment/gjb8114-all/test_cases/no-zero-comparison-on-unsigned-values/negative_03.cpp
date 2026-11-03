#include <iostream>

int main()
{
    unsigned int total = 0;
    bool is_negative = total < 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    return is_negative ? 1 : 0;
}
