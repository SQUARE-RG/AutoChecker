#include <cstdint>
#include <limits>
#include <stdexcept>

std::uint8_t checked_to_uint8(std::int64_t value) {
    if (value < 0 ||
        value > static_cast<std::int64_t>(std::numeric_limits<std::uint8_t>::max())) {
        throw std::out_of_range("value does not fit in uint8_t");
    }
    return static_cast<std::uint8_t>(value);
}

int main() {
    std::int64_t wide = 200;
    std::uint8_t narrow = checked_to_uint8(wide);
    (void)narrow;
    return 0;
}
