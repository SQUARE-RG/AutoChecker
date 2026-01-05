#include <stdio.h>

int main(void) {
    int num = 16, limit = 5;
    if (num >> 1 < limit) {  // 违反：右移和小于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Within limit\n");
    }
    return 0;
}