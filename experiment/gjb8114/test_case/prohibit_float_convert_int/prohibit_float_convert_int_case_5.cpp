#include <stdio.h>

int main(void) {
    float f1 = 2.5f, f2 = 3.5f;
    int i;
    i = f1 + f2;  // 违反：浮点表达式结果直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}