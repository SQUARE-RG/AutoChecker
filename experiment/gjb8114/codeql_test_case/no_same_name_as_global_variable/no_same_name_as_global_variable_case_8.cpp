#include <stdio.h>

int numbers[3] = {1, 2, 3};  // 全局数组

void test_array_shadowing(void) {
    int numbers[2] = {4, 5};  // 违反：局部数组与全局数组同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local array: %d, %d\n", numbers[0], numbers[1]);
}

int main(void) {
    test_array_shadowing();
    printf("Global array: %d, %d, %d\n", numbers[0], numbers[1], numbers[2]);
    return 0;
}