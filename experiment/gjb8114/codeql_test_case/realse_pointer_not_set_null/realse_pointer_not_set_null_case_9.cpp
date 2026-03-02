#include <stdlib.h>

void test_before_return(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 90;
        free(p);  // 违反：函数退出前释放但未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
    return;  // 虽然指针即将离开作用域，但良好习惯是显式置空
}

int main(void) {
    test_before_return();
    return 0;
}