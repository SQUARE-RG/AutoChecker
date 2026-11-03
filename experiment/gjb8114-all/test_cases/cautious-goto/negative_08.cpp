#include <exception>
#include <iostream>

int main() {
    int value = 0;
    try {
        if (value == 0) {
            goto after_try;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-5-1]
        }
        value = 10;
    } catch (const std::exception&) {
        value = -1;
    }
after_try:
    std::cout << value << '\n';
    return 0;
}
