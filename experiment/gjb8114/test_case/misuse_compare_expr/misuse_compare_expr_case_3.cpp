#include <stdio.h>

int main(void) {
    int p = 10, q = 5, r = 15;
    if (p ^ q != r) {  // 违反：异或和不等于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Condition met\n");
    }
    return 0;
}