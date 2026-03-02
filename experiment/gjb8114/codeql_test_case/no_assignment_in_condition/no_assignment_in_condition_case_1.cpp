#include <stdio.h>

int main(void) {
    int a = 0, b = 5;
    if (a = b) {  // 违反：在if条件中使用赋值语句
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        printf("a is now %d\n", a);
    }
    return 0;
}