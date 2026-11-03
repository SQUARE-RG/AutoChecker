#include <cstdint>

int main() {
    std::uint32_t x = 0x80000000u;
    std::uint32_t y = x >> 31;
    (void)y;
    return 0;
}
