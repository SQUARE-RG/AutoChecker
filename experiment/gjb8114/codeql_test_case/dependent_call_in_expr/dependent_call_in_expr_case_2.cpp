#include <stdio.h>

int add_value(int *x) {
    *x += 5;
    return *x;
}

int multiply_value(int *x) {
    *x *= 2;
    return *x;
}

int main(void) {
    int value = 10;
    int result = add_value(&value) * multiply_value(&value);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}