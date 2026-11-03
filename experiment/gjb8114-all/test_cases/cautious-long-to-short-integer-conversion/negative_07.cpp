#include <cstdint>

std::int64_t read_value() { return 4294967296; }

int main() {
    std::uint32_t values[1] = {0};
    std::int64_t wide = read_value();
    values[0] = wide; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
    return 0;
}
