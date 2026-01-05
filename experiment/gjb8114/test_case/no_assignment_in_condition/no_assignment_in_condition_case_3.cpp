#include <stdio.h>

int main(void) {
    int count = 5;
    int value;
    while (value = count--) {  // 违反：在while条件中使用赋值语句
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        printf("%d ", value);
    }
    return 0;
}