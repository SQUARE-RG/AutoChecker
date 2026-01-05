#include <stdlib.h>

void test_calloc_free(void) {
    int *p = (int*)calloc(1, sizeof(int));
    if (p != NULL) {
        *p = 70;
        free(p);  // 违反：calloc分配的内存释放后未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
}

int main(void) {
    test_calloc_free();
    return 0;
}