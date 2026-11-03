#include <cstddef>

int fun(int width);

int main()
{
    int i = fun(0);
    return 0;
}

int fun(int width)
{
    int w = width - 10;
    return w;
}
