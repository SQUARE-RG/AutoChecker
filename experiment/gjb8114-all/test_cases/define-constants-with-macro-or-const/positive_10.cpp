#include <chrono>

const int kTimeoutMilliseconds = 250;

std::chrono::milliseconds make_timeout() {
    return std::chrono::milliseconds(kTimeoutMilliseconds);
}

int main() {
    auto timeout = make_timeout();
    (void)timeout;
    return 0;
}
