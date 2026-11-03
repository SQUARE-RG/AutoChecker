#include <setjmp.h>

jmp_buf env;

int main() {
    for (; setjmp(env) == 0; ) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
        break;
    }
    return 0;
}
