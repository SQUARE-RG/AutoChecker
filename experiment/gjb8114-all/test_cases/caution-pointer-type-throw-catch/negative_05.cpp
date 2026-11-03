#include <iostream>

int main() {
    const int value = 42;
    try {
        throw &value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
    } catch (const int* ptr) {
        std::cout << "caught const pointer: " << *ptr << '\n';
    }
    return 0;
}
