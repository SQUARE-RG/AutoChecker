#include <iostream>

static int square(int value) { return value * value; }
static int negate(int value) { return -value; }

int (*ops[])(int) = { &square, &negate }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]

int main() {
    int index = 1;
    int value = 3;
    int result = ops[index](value);
    std::cout << result << '\n';
    return 0;
}
