#include <stdio.h>

int main(void) {
    float f = 10.5f;
    short s;
    s = f;  // 违反：float变量直接赋给short变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", s);
    return 0;
}