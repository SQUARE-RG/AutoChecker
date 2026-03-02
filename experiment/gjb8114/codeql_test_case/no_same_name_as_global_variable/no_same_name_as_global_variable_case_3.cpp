#include <stdio.h>

int data = 10;
float result = 3.14f;  // 全局变量

void test_multiple_shadowing(void) {
    int data = 20;      // 违反：第一个局部变量与全局变量同名
    float result = 2.71f;  // 违反：第二个局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local data: %d, result: %.2f\n", data, result);
}

int main(void) {
    test_multiple_shadowing();
    printf("Global data: %d, result: %.2f\n", data, result);
    return 0;
}