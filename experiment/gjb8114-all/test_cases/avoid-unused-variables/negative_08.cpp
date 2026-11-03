#include <iostream>
#include <stdexcept>

int main() {
    try {
        int unused = 7; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
        std::cout << "working\n";
    } catch (const std::exception& e) {
        std::cout << e.what() << '\n';
    }
    return 0;
}
