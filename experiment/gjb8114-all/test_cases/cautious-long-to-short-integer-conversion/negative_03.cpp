#include <cstdint>

void consume_short(std::int16_t value) {
    (void)value;
}

int main() {
    std::int64_t wide = 70000;
    consume_short(wide); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
    return 0;
}
