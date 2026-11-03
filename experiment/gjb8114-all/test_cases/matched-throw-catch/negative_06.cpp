#include <stdexcept>

int main() {
    try {
        try {
            throw 42;
        } catch (int) {
        }
        throw std::runtime_error("boom"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (std::logic_error&) {
    }
    return 0;
}
