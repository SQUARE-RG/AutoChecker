#include <stdio.h>

int main(void) {
    int a = 5, b = 3, c = 0;
    if (a > b) {
        if (c = a + b) {  // 违反：嵌套if条件中使用赋值语句
            // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
            printf("Sum is %d\n", c);
        }
    }
    return 0;
}