#include <cstdlib>

unsigned int pfun(unsigned int **pa);

int main()
{
    unsigned int *data = nullptr;
    unsigned int result = pfun(&data);
    return 0;
}

unsigned int pfun(unsigned int **pa)
{
    static unsigned int i = 10;
    i = i + 1;
    *pa = &i;
    return i;
}
