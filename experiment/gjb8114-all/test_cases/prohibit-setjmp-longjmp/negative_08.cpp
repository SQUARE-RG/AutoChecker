#include <setjmp.h>
#include <iostream>

jmp_buf checkpoint;

int main() {
    int rounds = 0;
    while (setjmp(checkpoint) == 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
        ++rounds;
        std::cout << "round " << rounds << '\n';
        break;
    }
    return 0;
}
