// File: negative_one_of_two.c
#include <stdlib.h>
void test_two_pointers(void) {
    int *p1 = (int*)malloc(sizeof(int));
    int *p2 = (int*)malloc(sizeof(int));
    if (p1 != NULL) { *p1 = 1; } // p1 被正确检查
    *p2 = 2; 
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}