#include <stdlib.h>

int *p = NULL;
void foo(void)
{
    p = (int*) malloc(sizeof(int));
    *p = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}