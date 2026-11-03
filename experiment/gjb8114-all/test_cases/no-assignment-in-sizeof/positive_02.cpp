#include <cstddef>

int main()
{
    int x = 1;
    int y = 2;
    std::size_t ilen = sizeof(x + y);
    (void)x;
    (void)y;
    (void)ilen;
    return 0;
}
