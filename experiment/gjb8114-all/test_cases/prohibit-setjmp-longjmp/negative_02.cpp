#include <setjmp.h>

[[noreturn]] void jump_back(jmp_buf env)
{
    longjmp(env, 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
}

int main()
{
    return 0;
}
