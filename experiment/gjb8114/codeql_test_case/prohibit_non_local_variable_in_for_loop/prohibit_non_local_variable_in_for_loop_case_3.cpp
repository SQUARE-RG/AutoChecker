#include <stdio.h>

extern int external_var;  // 外部声明变量
int external_var = 0;     // 实际定义

int main(void) {
    for (external_var = 0; external_var < 4; external_var++) {  // 违反：使用外部变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", external_var);
    }
    return 0;
}