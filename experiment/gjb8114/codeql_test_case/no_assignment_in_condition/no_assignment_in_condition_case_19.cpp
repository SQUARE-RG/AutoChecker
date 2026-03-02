#include <stdio.h>

int main(void) {
    int a = 5, b = 3;
    int max = (a > b) ? a : b;  // 符合：三元运算符中不使用赋值
    printf("Max is %d\n", max);
    return 0;
}