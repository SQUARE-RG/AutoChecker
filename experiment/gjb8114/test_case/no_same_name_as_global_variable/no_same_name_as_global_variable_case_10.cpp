#include <stdio.h>

int level = 0;  // 全局变量

void test_nested_shadowing(void) {
    int level = 1;  // 外层局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    
    if (level > 0) {
        int level = 2;  // 内层局部变量与外层局部变量同名（允许，但外层已违规）
        printf("Inner level: %d\n", level);
    }
    printf("Outer level: %d\n", level);
}

int main(void) {
    test_nested_shadowing();
    printf("Global level: %d\n", level);
    return 0;
}