#include <stdio.h>

int main(void) {
    int flag = 1;
    int value = 0;
    do {
        value++;
        printf("%d ", value);
    } while (flag = 0);  // 违反：在do-while条件中使用赋值语句
    // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
    return 0;
}