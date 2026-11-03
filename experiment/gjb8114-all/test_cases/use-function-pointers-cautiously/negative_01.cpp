#include <iostream>

int square(int value) {
    return value * value;
}

int main() {
    int (*function_pointer)(int) = &square; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]
    std::cout << function_pointer(5) << '\n';
    return 0;
}
