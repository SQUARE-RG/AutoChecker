#include <stdio.h>

int main(void) {
    double d = 5.67;
    int i;
    i = d;  // 违反：double变量直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}