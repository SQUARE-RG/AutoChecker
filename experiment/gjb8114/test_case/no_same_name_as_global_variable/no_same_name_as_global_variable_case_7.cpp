#include <stdio.h>

int* pointer = NULL;  // 全局指针变量

void test_pointer_shadowing(void) {
    int value = 5;
    int* pointer = &value;  // 违反：局部指针变量与全局指针变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Local pointer value: %d\n", *pointer);
}

int main(void) {
    int x = 10;
    pointer = &x;
    test_pointer_shadowing();
    printf("Global pointer value: %d\n", *pointer);
    return 0;
}