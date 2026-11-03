#include <iostream>

enum class ErrorCode { Bad, Worse };

int main() {
    try {
        throw ErrorCode::Bad; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (int) {
        std::cout << "int caught" << std::endl;
    }
    return 0;
}
