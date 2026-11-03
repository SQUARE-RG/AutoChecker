#include <cstdint>

template <typename T>
constexpr T bounded(T value, T lo, T hi)
{
    return (value < lo) ? lo : ((hi < value) ? hi : value);
}

#define BOUNDED(v, lo, hi) bounded((v), (lo), (hi))

int main()
{
    int x = 42;
    int y = BOUNDED(x, 0, 10);
    return y;
}
