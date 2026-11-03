#include <exception>

int main() {
    try {
        throw "error"; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (const std::exception&) {
    }
    return 0;
}
