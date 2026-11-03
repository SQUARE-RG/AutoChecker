#include <cstdint>
#include <limits>

std::uint16_t checked_uint16(std::int64_t value) {
    if (value < 0 || value > std::numeric_limits<std::uint16_t>::max()) {
        return 0;
    }
    return static_cast<std::uint16_t>(value);
}
