#include <string>

int main() {
    try {
        throw 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (const std::string&) {
    }
    return 0;
}
