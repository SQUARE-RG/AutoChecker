#include <stdio.h>

int main(void) {
    int a = 20, b = 10, result = 5;
    if (a - b != result) {  // 违反：减法和不等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Difference is not equal\n");
    }
    return 0;
}