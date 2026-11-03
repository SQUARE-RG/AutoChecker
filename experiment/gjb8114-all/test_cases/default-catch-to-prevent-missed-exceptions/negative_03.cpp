#include <stdexcept>

int main() {
    auto handler = [] {
        try {
            throw std::runtime_error("boom");
        } catch (const std::runtime_error& e) {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
            (void)e;
        }
    };
    handler();
    return 0;
}
