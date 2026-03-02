#include <stdio.h>

int *global_ptr = NULL;  // 全局指针变量
int array[5] = {1, 2, 3, 4, 5};

int main(void) {
    int value = 10;
    global_ptr = &value;
    
    for (*global_ptr = 0; *global_ptr < 3; (*global_ptr)++) {  // 违反：使用全局指针变量作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", *global_ptr);
    }
    return 0;
}