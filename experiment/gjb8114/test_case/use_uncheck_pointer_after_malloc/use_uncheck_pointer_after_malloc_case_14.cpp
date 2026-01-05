#include <stdlib.h>

void foo()
{
    int *p = (int*) malloc(sizeof(int));
    if (!p)
        return;
    p[0] = 1;
}

void bar()
{
    int *p = (int*) malloc(sizeof(int));
    if (p) p[0] = 1;
}

void func()
{
    int *p = (int*) malloc(sizeof(int));
    bool failed = !p;
    if (!failed) p[0] = 1;
}

void explict_cast_func()
{
    int *p = (int*) malloc(sizeof(int));
    if (static_cast<bool>(p)) p[0] = 1;
}