#include <cstdint>

int main() {
    std::int16_t total = 0;
    std::int64_t delta = 50000;
    total += delta; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
    (void)total;
    return 0;
}
