#include <cstdint>
#include <limits>
#include <iostream>

bool narrowToInt32Safely(std::int64_t value, std::int32_t& result) {
    const std::int64_t lower = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::min());
    const std::int64_t upper = static_cast<std::int64_t>(std::numeric_limits<std::int32_t>::max());
    if (value < lower || value > upper) {
        return false;
    }
    result = static_cast<std::int32_t>(value);
    return true;
}

int main() {
    std::int32_t result = 0;
    if (narrowToInt32Safely(static_cast<std::int64_t>(1000), result)) {
        std::cout << result << std::endl;
    }
    return 0;
}
