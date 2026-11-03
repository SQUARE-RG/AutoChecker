#include <exception>
#include <iostream>
#include <stdexcept>

int main() {
    try {
        throw std::runtime_error("failure");
    }
    catch (std::exception e) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
    {
        std::cout << e.what() << '\n';
    }
    return 0;
}
