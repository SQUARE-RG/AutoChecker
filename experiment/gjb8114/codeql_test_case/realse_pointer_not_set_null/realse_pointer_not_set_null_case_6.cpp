#include <stdlib.h>

void test_multiple_allocations(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 60;
        free(p);
        p = NULL;  // 第一次正确置空
        
        p = (int*)malloc(sizeof(int) * 2);  // 重新分配
        if (p != NULL) {
            p[0] = 1;
            p[1] = 2;
            free(p);  // 违反：第二次释放后未置空
            // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
        }
    }
}

int main(void) {
    test_multiple_allocations();
    return 0;
}