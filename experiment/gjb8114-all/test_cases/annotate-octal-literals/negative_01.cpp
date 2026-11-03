#include <cstddef>

int main()
{
    int code[3];
    code[0] = 109;
    code[1] = 100;
    code[2] = 011; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-4]
    return 0;
}
