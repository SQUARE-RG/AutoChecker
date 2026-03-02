#include <stdio.h>

int main(void) {
    int total = 100, divisor = 5, max_quotient = 25;
    if (total / divisor <= max_quotient) {  // 违反：除法和小于等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Quotient is within limit\n");
    }
    return 0;
}