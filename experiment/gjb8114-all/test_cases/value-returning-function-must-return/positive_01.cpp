#include <cstdlib>

int adjust(int a, int *b)
{
    if (1 == a)
    {
        *b = *b + a;
        return 1;
    }
    else
    {
        *b = *b - a;
        return 0;
    }
}

int main(void)
{
    int i = 1;
    int j = 2;
    return adjust(i, &j) + j;
}
