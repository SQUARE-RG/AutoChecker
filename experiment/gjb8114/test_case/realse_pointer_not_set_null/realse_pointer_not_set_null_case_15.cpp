#include <stdlib.h>

void test_proper_calloc_free(void) {
    int *p = (int*)calloc(1, sizeof(int));
    if (p != NULL) {
        *p = 50;
        free(p);
        p = NULL;  // 符合：calloc分配的内存释放后置空
    }
}

int main(void) {
    test_proper_calloc_free();
    return 0;
}