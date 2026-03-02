// File: positive_used_in_condition.c
#include <stdlib.h>
#include <stdbool.h>
void test_in_condition(void) {
    int *p = (int*)malloc(sizeof(int));
    bool isValid = (p != NULL);
    if (isValid) {
        *p = 1;
    }
}