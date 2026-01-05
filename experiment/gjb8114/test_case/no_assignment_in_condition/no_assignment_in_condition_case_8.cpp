#include <stdio.h>

int get_value(void) {
    return 10;
}

int main(void) {
    int result;
    if (result = get_value()) {  // 违反：在条件中使用赋值语句接收函数返回值
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        printf("Result: %d\n", result);
    }
    return 0;
}