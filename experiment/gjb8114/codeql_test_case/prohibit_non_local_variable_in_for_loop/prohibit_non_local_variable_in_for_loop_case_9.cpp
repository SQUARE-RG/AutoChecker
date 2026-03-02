#include <stdio.h>

int outer_var = 0;  // 全局变量

void outer_function(void) {
    for (outer_var = 0; outer_var < 3; outer_var++) {  // 违反：外层函数使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("Outer: %d\n", outer_var);
    }
}

int main(void) {
    outer_function();
    return 0;
}