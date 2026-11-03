#include <cstdint>
#include <optional>
#include <algorithm>

std::int64_t read_value() { return 300; }

int main() {
    std::int64_t wide = read_value();
    std::uint8_t clamped = static_cast<std::uint8_t>(
        std::clamp<std::int64_t>(wide, 0, 255));
    std::optional<std::uint8_t> narrowed = clamped;
    return 0;
}
