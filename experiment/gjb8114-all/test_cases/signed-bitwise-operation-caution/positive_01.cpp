#include <cstdint>

int main() {
    std::uint32_t value = 1u;
    std::uint32_t shifted = value << 4u;
    (void)shifted;
    return 0;
}
