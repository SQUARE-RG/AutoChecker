#include <cstdint>
#include <optional>

std::int64_t read_value() { return 300; }

int main() {
    std::int64_t wide = read_value();
    std::optional<std::uint8_t> narrowed = wide; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
    return 0;
}
