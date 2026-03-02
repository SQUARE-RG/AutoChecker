#include <stdlib.h>

void test_proper_malloc_free(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 10;
        free(p);
        p = NULL;  // 符合：释放后立即置空
    }
}

int main(void) {
    test_proper_malloc_free();
    return 0;
}