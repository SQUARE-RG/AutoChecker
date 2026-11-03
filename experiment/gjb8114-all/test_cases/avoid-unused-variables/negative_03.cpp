#include <iostream>

int main() {
    int value = 5;
    if (value > 0) {
        const int unused = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
    }
    std::cout << value << '\n';
    return 0;
}
