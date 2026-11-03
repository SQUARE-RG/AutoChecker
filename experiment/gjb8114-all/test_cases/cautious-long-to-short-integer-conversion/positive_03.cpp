#include <cstdint>
#include <limits>
#include <stdexcept>

std::int8_t checked_to_int8(std::int64_t value) {
    if (value < std::numeric_limits<std::int8_t>::min() ||
        value > std::numeric_limits<std::int8_t>::max()) {
        throw std::out_of_range("value does not fit in int8_t");
    }
    return static_cast<std::int8_t>(value);
}

int main() {
    std::int64_t wide = 42;
    std::int8_t narrow = checked_to_int8(wide);
    (void)narrow;
    return 0;
}
