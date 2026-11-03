#include <cstdint>

int main()
{
    std::uint64_t x = 1ULL;
    x <<= 16;
    return static_cast<int>(x);
}
