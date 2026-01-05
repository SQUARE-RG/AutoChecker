#include <stdio.h>

static int static_counter = 0;  // 静态全局变量

int main(void) {
    for (static_counter = 0; static_counter < 3; static_counter++) {  // 违反：使用静态全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", static_counter);
    }
    return 0;
}