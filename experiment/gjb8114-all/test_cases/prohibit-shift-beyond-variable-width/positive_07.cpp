#include <cstdint>

int main()
{
    std::int32_t x = 0x7fffffff;
    std::int32_t y = x >> 5;
    return y;
}
