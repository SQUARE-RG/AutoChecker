#include <stdio.h>

int main(void) {
    float arr[3] = {1.1f, 2.2f, 3.3f};
    int i;
    i = arr[1];  // 违反：浮点数组元素直接赋给int变量未使用强制转换
    // CHECK-MESSAGES: 禁止浮点数变量赋给整型变量 [gjb8114-r-1-10-1]
    printf("%d\n", i);
    return 0;
}