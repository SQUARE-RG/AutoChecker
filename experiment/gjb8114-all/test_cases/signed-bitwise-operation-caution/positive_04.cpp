#include <cstdint>

int main() {
    std::uint16_t value = 0x00FF;
    std::uint16_t mask = 0x0F0F;
    std::uint16_t result = value & mask;
    return result == 0x000F ? 0 : 1;
}
