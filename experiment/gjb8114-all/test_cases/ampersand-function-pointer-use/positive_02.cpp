#include <cstdlib>

int fun(int value);
int apply(int (*fp)(int), int value);

int main()
{
    return apply(&fun, 3);
}

int apply(int (*fp)(int), int value)
{
    return fp(value);
}

int fun(int value)
{
    return value + 1;
}
