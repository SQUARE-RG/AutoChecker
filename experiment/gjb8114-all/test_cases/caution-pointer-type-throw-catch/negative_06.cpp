#include <iostream>

int main() {
    int value = 7;
    int* ptr = &value;
    try {
        throw &ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
    } catch (int** pptr) {
        std::cout << "caught pointer-to-pointer: " << *(*pptr) << '\n';
    }
    return 0;
}
