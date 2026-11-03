#include <cstdlib>

int sub(int a, int b)
{
    return a - b;
}

int main()
{
    int (*handlers[1])(int, int) = {&sub};
    int result = handlers[0](3, 1);
    return result == 2 ? 0 : 1;
}
