#include <stdio.h>

int global_index = 0;  // 全局索引变量
int data[5] = {10, 20, 30, 40, 50};

int main(void) {
    for (global_index = 0; global_index < 5; global_index++) {  // 违反：使用全局变量作为数组遍历的控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", data[global_index]);
    }
    return 0;
}