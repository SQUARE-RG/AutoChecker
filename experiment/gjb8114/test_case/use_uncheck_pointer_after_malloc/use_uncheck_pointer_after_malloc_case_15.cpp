#include <stdlib.h>
#include <stdbool.h>

void foo(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (!p)
        return;
    p[0] = 1;
}

void bar(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (p) {
        p[0] = 1;
    }
}

void func(void)
{
    int *p = (int*) malloc(sizeof(int));
    bool good = p;
    if (good) p[0] = 1;
}

void explict_cast_func(void)
{
    int *p = (int*) malloc(sizeof(int));
    if ((bool)p) p[0] = 1;
}

void double_negative_func(void)
{
    int *p = (int*) malloc(sizeof(int));
    if (!!p) p[0] = 1;
}