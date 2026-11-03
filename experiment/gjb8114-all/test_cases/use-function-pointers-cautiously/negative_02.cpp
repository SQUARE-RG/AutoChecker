#include <iostream>

int increment(int value) {
    return value + 1;
}

int apply(int (*callback)(int), int value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]
    return callback(value);
}

int main() {
    std::cout << apply(&increment, 4) << '\n';
    return 0;
}
