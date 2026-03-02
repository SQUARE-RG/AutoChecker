#include <stdio.h>

float get_value(void) {
    return 7.89f;
}

int main(void) {
    int i;
    i = get_value();  // 违反：函数返回的float值直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}