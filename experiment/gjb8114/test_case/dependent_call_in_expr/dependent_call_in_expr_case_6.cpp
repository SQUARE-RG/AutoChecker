#include <stdio.h>

int x = 5;

int increment_x(void) {
    x++;
    return x;
}

int check_x(void) {
    return x > 10;
}

int main(void) {
    int result = (increment_x() > 0) && check_x();  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}