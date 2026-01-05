// File: positive_free_no_use.c
#include <stdlib.h>
void test_free(void) {
    int *p = (int*)malloc(sizeof(int));
    free(p); // 释放前未使用
}