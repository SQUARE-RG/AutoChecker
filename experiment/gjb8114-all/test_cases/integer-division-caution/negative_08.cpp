#include <cstddef>

std::size_t average(std::size_t total, std::size_t count) {
    std::size_t result = 0;
    result = total / count; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
    return result;
}

int main() {
    std::size_t total = 20;
    std::size_t count = 3;
    return static_cast<int>(average(total, count));
}
