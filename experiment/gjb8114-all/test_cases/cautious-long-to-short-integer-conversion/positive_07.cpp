#include <cstdint>
#include <limits>

std::int64_t read_value() { return 42; }

int main() {
    std::uint32_t values[1] = {0};
    std::int64_t wide = read_value();
    if (wide < 0 ||
        wide > static_cast<std::int64_t>(std::numeric_limits<std::uint32_t>::max())) {
        return 1;
    }
    values[0] = static_cast<std::uint32_t>(wide);
    return 0;
}
