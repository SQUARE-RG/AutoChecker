#include <cstdint>
#include <limits>
#include <vector>

void record_checked(std::vector<std::int32_t>& samples, std::int64_t value) {
    constexpr std::int64_t kMin = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::min());
    constexpr std::int64_t kMax = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::max());
    if (value < kMin || value > kMax) {
        return;
    }
    samples.push_back(static_cast<std::int32_t>(value));
}
