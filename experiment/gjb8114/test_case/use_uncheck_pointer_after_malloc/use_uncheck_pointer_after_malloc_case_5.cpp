#include <stdlib.h>
void foo(void)
{
    int *pa = NULL;
    pa = (int*) malloc(sizeof(int) * 2);
    int *pb = (int*) malloc(sizeof(int) * 2);
    pa[0] = 1;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    pa[1] = 2;
    pb[0] = 3;
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
    pb[1] = 4;
}