#include <stdio.h>

int global_var = 0;

int main(void) {
    if (global_var = 1) {  // 违反：全局变量在条件中使用赋值语句
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        printf("Global var set to 1\n");
    }
    return 0;
}