#include <cstdint>
#include <vector>

void record_measurement(std::vector<std::int32_t>& samples, std::int64_t value) {
    samples.push_back(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-3]
}
