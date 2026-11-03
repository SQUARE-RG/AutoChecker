#include <cstddef>

int main()
{
    int x = 1;
    int y = 2;
    std::size_t ilen;
    x = y;
    ilen = sizeof(x);
    (void)ilen;
    return 0;
}
