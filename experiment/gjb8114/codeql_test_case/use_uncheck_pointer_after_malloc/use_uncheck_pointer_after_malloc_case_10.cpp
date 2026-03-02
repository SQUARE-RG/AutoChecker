// File: negative_basic_malloc.c
#include <stdlib.h>
void test_basic(void) {
    int *p = (int*)malloc(sizeof(int));
    *p = 10; 
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}