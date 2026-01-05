#include <stdlib.h>

void test_basic_malloc_free(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 10;
        free(p);  // 违反：释放后未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
}

int main(void) {
    test_basic_malloc_free();
    return 0;
}