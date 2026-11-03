#include <cstdio>
#include <setjmp.h>

namespace {
jmp_buf g_jump;
}

int main()
{
    int code = setjmp(g_jump);
    if (code != 0) {
        std::puts("recovered from longjmp");
        return 0;
    }

    auto bail_out = []() {
        std::puts("bailing out");
        longjmp(g_jump, 7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
    };

    bail_out();
    return 0;
}
