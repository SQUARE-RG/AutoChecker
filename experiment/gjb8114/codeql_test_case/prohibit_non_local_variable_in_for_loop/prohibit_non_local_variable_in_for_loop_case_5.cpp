#include <stdio.h>

int shared_counter = 0;  // 全局变量

void func1(void) {
    for (shared_counter = 0; shared_counter < 2; shared_counter++) {  // 违反：多个函数共享的全局变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("Func1: %d\n", shared_counter);
    }
}

int main(void) {
    func1();
    return 0;
}