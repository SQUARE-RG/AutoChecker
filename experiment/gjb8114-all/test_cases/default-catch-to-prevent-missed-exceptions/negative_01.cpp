#include <exception>
#include <stdexcept>

int main() {
    try {
        throw std::runtime_error("example");
    } catch (const std::exception&) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
        return 1;
    }
    return 0;
}
