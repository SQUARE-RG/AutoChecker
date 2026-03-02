// File: negative_global_pointer.c
#include <stdlib.h>
int *global_ptr = NULL;
void test_global(void) {
    global_ptr = (int*)malloc(sizeof(int));
    *global_ptr = 5; 
    // CHECK-MESSAGES: :[[@LINE]]:9: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}