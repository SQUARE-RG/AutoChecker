#include <stdexcept>

void handle(int code) {
    try {
        if (code == 1) {
            throw std::runtime_error("one");
        }
        throw std::logic_error("other");
    } catch (const std::runtime_error& error1) {
        (void)error1;
    } catch (const std::logic_error& errorl) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
        (void)errorl;
    }
}

int main() {
    handle(1);
    handle(0);
    return 0;
}
