#include <stdio.h>

int global_i = 0;  // 全局变量

int main(void) {
    for (global_i = 0; global_i < 5; global_i++) {  // 违反：使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", global_i);
    }
    return 0;
}