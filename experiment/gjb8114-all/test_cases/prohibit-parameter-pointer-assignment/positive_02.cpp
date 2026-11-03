#include <cstddef>

void assign_value(int *p, int v)
{
    *p = v;
}

int main()
{
    int value = 0;
    assign_value(&value, 42);
    return 0;
}
