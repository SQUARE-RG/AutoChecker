#include <chrono>

std::chrono::milliseconds make_timeout() {
    return std::chrono::milliseconds(250);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
}

int main() {
    auto timeout = make_timeout();
    (void)timeout;
    return 0;
}
