#include <cstdint>

std::int16_t to_int16(std::int64_t value) {
    return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
}
