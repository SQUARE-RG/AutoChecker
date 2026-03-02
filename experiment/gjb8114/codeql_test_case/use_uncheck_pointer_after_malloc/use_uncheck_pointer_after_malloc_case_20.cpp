// File: positive_realloc_checked.c
#include <stdlib.h>
void test_safe_realloc(void) {
    int *p = (int*)malloc(sizeof(int));
    if (!p) return;
    int *new_p = (int*)realloc(p, sizeof(int) * 2);
    if (new_p != NULL) {
        new_p[1] = 2;
        p = new_p;
    } else {
        free(p);
    }
}