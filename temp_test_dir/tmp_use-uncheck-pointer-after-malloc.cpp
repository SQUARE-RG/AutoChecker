// File: positive_c_shorthand.c
#include <stdlib.h>
void test_c_shorthand(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p) {
        *p = 1;
    }
}