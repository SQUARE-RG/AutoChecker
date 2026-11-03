#include <cstdint>

int main() {
    std::uint32_t flags = 0xF0u;
    std::uint32_t inverted = ~flags;
    (void)inverted;
    return 0;
}
