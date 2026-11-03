#include <iostream>

int square(int value) {
    return value * value;
}

int (*global_transform)(int) = &square; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]

int main() {
    int input = 5;
    int result = global_transform(input);
    std::cout << result << std::endl;
    return 0;
}
