#include <iostream>

int main() {
    try {
        throw "error";  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
    } catch (const char* message) {
        std::cout << message << std::endl;
    }
    return 0;
}
