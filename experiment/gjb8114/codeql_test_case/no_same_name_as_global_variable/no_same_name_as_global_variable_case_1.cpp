#include <stdio.h>

int counter = 0;  // 全局变量

void test_basic_shadowing(void) {
    int counter = 5;  // 违反：局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local counter: %d\n", counter);
}

int main(void) {
    test_basic_shadowing();
    printf("Global counter: %d\n", counter);
    return 0;
}