#include <stdio.h>

int main(void) {
    double d = 123.456;
    long l;
    l = d;  // 违反：double变量直接赋给long变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%ld\n", l);
    return 0;
}