#include <stdlib.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (p != NULL)
    {
        *p = 1;
    }
}