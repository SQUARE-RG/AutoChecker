#include <exception>
#include <iostream>
#include <stdexcept>

int main() {
    try {
        throw std::exception(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (std::runtime_error &e) {
        std::cout << e.what() << std::endl;
    }
    return 0;
}
