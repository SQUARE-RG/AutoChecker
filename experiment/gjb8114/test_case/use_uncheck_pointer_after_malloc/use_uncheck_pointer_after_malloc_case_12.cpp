#include <stdlib.h>
void foo(void)
{
    int *p = NULL;
    p = (int*) malloc(sizeof(int));
    p = (int*) malloc(sizeof(int));
}