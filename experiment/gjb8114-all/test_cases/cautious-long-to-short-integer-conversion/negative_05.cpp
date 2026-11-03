#include <cstdint>

std::uint16_t to_uint16(std::int64_t value) {
    std::uint16_t result = (std::uint16_t)value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
    return result;
}
