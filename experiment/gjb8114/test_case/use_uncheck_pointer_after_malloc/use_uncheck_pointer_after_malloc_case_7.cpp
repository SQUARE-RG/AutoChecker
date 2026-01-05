// File: negative_struct_member.c
#include <stdlib.h>
struct Container {
    int *data_ptr;
};
void test_struct(void) {
    struct Container c;
    c.data_ptr = (int*)malloc(sizeof(int));
    *(c.data_ptr) = 42; 
    // CHECK-MESSAGES: :[[@LINE]]:10: warning: 禁止动态分配的指针变量未检查即使用 [gjb8114-r-1-3-8]
}