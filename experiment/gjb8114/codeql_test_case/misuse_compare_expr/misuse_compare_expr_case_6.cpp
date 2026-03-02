#include <stdio.h>

int main(void) {
    int x = 3, y = 4, sum = 7;
    if (x + y == sum) {  // 违反：加法和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Sum is correct\n");
    }
    return 0;
}