#include <cstdint>
#include <limits>
#include <iostream>

std::int16_t clampToInt16(std::int64_t value) {
    const std::int64_t lower = static_cast<std::int64_t>(std::numeric_limits<std::int16_t>::min());
    const std::int64_t upper = static_cast<std::int64_t>(std::numeric_limits<std::int16_t>::max());
    if (value < lower) {
        return std::numeric_limits<std::int16_t>::min();
    }
    if (value > upper) {
        return std::numeric_limits<std::int16_t>::max();
    }
    return static_cast<std::int16_t>(value);
}

int main() {
    std::int64_t value = 123456789LL;
    std::cout << clampToInt16(value) << std::endl;
    std::cout << clampToInt16(static_cast<std::int64_t>(-42)) << std::endl;
    return 0;
}
