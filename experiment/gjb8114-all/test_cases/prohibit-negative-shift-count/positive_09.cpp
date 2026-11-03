#include <cstdint>

int main()
{
    std::uint32_t value = 0x80000000u;
    int mask = 7;
    value >>= (mask & 3);
    return 0;
}
