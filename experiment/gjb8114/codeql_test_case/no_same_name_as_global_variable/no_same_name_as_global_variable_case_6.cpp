#include <stdio.h>

int count = 0;  // 全局变量

void test_static_shadowing(void) {
    static int count = 0;  // 违反：静态局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    count++;
    printf("Static count: %d\n", count);
}

int main(void) {
    test_static_shadowing();
    printf("Global count: %d\n", count);
    return 0;
}