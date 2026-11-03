#include <cstdint>
#include <limits>
#include <optional>

std::optional<std::int16_t> checked_int16(std::int64_t value) {
    if (value < std::numeric_limits<std::int16_t>::min() ||
        value > std::numeric_limits<std::int16_t>::max()) {
        return std::nullopt;
    }
    return static_cast<std::int16_t>(value);
}
