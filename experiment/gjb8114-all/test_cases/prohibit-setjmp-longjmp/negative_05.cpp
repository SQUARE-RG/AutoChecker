#include <csetjmp>

std::jmp_buf g_env;

class Aborter {
public:
    void abort_now() {
        std::longjmp(g_env, 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
    }
};

int main() {
    Aborter a;
    (void)a;
    return 0;
}
