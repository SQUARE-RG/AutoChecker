#include <setjmp.h>

jmp_buf state_env;

int classify_state() {
    switch (setjmp(state_env)) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
        case 0:
            return 1;
        default:
            return 2;
    }
    return 0;
}

int main() {
    return classify_state();
}
