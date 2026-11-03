#include <cstddef>

int main()
{
    int x = 1, y = 2;
    std::size_t ilen = sizeof((x, y));
    x = y;
    return 0;
}
