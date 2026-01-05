#include <stdio.h>

int main(void) {
    int width = 5, height = 3, area_limit = 20;
    if (width * height >= area_limit) {  // 违反：乘法和大于等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Area meets or exceeds limit\n");
    }
    return 0;
}