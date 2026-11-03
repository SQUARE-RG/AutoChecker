#include <cstddef>

int main()
{
    int x = 1, y = 2;
    x = y;
    std::size_t ilen = sizeof(static_cast<long>(x));
    return 0;
}
