#include <stdio.h>

int main(void) {
    int number = 7, mod = 3, expected = 1;
    if (number % mod == expected) {  // 违反：取模和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Remainder is as expected\n");
    }
    return 0;
}