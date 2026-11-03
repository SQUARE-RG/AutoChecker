#include <setjmp.h>

int main()
{
    jmp_buf env;
    int result = setjmp(env); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
    return result == 0 ? 0 : 1;
}
