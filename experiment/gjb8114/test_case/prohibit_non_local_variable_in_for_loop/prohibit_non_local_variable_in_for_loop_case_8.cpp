#include <stdio.h>

int i = 0;  // 全局变量

void foo(void) {
    for (i = 0; i < 7; ++i) {  // 违反：使用全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", i);
    }
}

int main(void) {
    foo();
    return 0;
}