#include <stdio.h>

int main(void) {
    int a = 0, b = 0, c = 5;
    if (a == 0 || (b = c)) {  // 违反：在逻辑或表达式中使用赋值语句
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        printf("b is %d\n", b);
    }
    return 0;
}