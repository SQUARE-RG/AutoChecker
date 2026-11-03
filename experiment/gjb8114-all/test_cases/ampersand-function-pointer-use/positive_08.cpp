#include <cstdlib>

int sub(int a, int b)
{
    return a - b;
}

struct Operation
{
    int (*func)(int, int);
};

int main()
{
    Operation op = {&sub};
    int result = op.func(3, 1);
    return result == 2 ? 0 : 1;
}
