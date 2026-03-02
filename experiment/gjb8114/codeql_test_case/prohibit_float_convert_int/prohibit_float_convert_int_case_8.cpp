#include <stdio.h>

double global_d = 15.75;

int main(void) {
    int i;
    i = global_d;  // 违反：全局double变量直接赋给局部int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}