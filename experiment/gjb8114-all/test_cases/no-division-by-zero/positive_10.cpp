#include <cstddef>

int main()
{
    int a = 48;
    std::size_t divisor = alignof(double);
    std::size_t c = a / divisor;
    return static_cast<int>(c);
}
