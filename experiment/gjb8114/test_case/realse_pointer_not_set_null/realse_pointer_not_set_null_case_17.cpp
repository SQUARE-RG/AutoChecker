#include <stdlib.h>

void test_proper_realloc(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 80;
        int *new_p = (int*)realloc(p, sizeof(int) * 3);
        if (new_p != NULL) {
            p = new_p;
        }
        free(p);
        p = NULL;  // 符合：realloc后显式置空
    }
}

int main(void) {
    test_proper_realloc();
    return 0;
}