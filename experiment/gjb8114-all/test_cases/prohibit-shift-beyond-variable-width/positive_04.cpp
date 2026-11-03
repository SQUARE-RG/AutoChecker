#include <cstdint>

int main() {
    std::uint64_t x = 1ull;
    std::uint64_t y = x << 32;
    (void)y;
    return 0;
}
