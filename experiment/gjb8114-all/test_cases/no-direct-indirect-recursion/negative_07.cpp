#include <cstdint>

static int recurse_sum(int n) {
    using RecursiveFn = int (*)(int);
    RecursiveFn self = &recurse_sum;
    if (n <= 0) {
        return 0;
    }
    return n + self(n - 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
}

int main() {
    return recurse_sum(5);
}
