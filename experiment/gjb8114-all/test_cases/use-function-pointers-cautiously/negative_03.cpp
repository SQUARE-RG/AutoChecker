#include <iostream>

static int increment(int value) { return value + 1; }

struct Operation {
    int (*handler)(int) = &increment; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]
};

int main() {
    Operation op;
    int result = op.handler(4);
    std::cout << result << '\n';
    return 0;
}
