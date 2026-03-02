#include <stdio.h>

int main(void) {
    int value = 2, threshold = 10;
    if (value << 2 > threshold) {  // 违反：左移和大于运算符未使用括号
        // CHECK-MESSAGES: 禁止比较表达式中的运算项未使用括号 [gjb8114-r-1-2-5]
        printf("Value exceeds threshold\n");
    }
    return 0;
}