#include <stdlib.h>

void test_realloc_scenario(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 80;
        int *new_p = (int*)realloc(p, sizeof(int) * 3);
        if (new_p != NULL) {
            p = new_p;  // realloc成功后，原指针p已被realloc处理
            free(p);    // 但良好的习惯是显式置空，这里违反规则
            // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
        }
    }
}

int main(void) {
    test_realloc_scenario();
    return 0;
}