#include <setjmp.h>

jmp_buf env;

int main(int argc, char**) {
    if (argc > 1) {
        longjmp(env, 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
    }
    return 0;
}
