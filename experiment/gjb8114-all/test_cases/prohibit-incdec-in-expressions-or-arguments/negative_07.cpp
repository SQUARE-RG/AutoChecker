#include <iostream>

int compute(int value) {
    return value * 2;
}

int main() {
    int x = 5;
    int result = compute(--x); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    std::cout << result << std::endl;
    return 0;
}
