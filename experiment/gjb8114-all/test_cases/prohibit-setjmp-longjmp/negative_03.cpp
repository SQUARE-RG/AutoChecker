#include <cstdio>
#include <setjmp.h>

namespace {
jmp_buf g_env;
}

int safe_divide(int a, int b, int* out)
{
    if (b == 0) {
        return -1;
    }
    *out = a / b;
    return 0;
}

int main()
{
    int result = 0;
    int rc = 0;

    rc = setjmp(g_env); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
    if (rc == 0) {
        if (safe_divide(10, 0, &result) != 0) {
            std::puts("division failed");
        }
    }

    return rc;
}
