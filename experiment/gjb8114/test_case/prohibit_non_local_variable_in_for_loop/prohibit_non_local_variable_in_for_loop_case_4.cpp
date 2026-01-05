#include <stdio.h>

int file_scope_var = 0;  // 文件作用域变量

void process_data(void) {
    for (file_scope_var = 0; file_scope_var < 5; file_scope_var++) {  // 违反：使用文件作用域变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", file_scope_var);
    }
}

int main(void) {
    process_data();
    return 0;
}