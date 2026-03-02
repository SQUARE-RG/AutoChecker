#include <stdio.h>

int main(void) {
    int x = 5, y = 3, z = 1;
    if (x & y == z) {  // 违反：位与和等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Condition met\n");
    }
    return 0;
}