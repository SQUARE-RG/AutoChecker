#include <iostream>

int main() {
    int value = 42;
    int* ptr = &value;
    try {
        throw ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (char*) {
        std::cout << "char pointer caught" << std::endl;
    }
    return 0;
}
