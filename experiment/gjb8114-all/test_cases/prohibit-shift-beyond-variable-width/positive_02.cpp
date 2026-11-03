#include <cstdint>

int main()
{
    std::uint64_t x = 0x8000000000000000ULL;
    std::uint64_t y = x >> 63;
    (void)y;
    return 0;
}
