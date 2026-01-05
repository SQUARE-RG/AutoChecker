#include <stdio.h>

int main(void) {
    int a = 6, b = 2, c = 2;
    if (a | b == c) {  // 违反：位或和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Condition met\n");
    }
    return 0;
}