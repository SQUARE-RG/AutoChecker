// File: positive_unused.c
#include <stdlib.h>
void test_unused(void) {
    int *p = (int*)malloc(sizeof(int));
    // 指针 p 未被使用
}