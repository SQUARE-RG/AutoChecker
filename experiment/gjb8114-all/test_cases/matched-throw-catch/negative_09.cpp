#include <iostream>
#include <stdexcept>

int main() {
    int i = 1;
    try {
        switch (i) {
            case 1:
                throw std::out_of_range("first"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
            case 2:
                throw std::overflow_error("second");
            default:
                break;
        }
    } catch (const std::overflow_error& e) {
        std::cout << e.what() << std::endl;
    }
    return 0;
}
