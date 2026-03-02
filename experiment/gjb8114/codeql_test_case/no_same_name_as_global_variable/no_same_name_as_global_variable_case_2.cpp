#include <stdio.h>

int value = 100;  // 全局变量

void process_value(int value) {  // 违反：函数参数与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    printf("Parameter value: %d\n", value);
}

int main(void) {
    process_value(50);
    printf("Global value: %d\n", value);
    return 0;
}