#include <iostream>

enum class Mode { Off, On };

int main() {
    Mode mode; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
    mode = Mode::On;

    if (mode == Mode::On) {
        std::cout << 1 << std::endl;
    } else {
        std::cout << 0 << std::endl;
    }

    return 0;
}
