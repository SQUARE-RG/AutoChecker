#include <stdio.h>

int main(void) {
    float f = 4.5f;
    double d = 2.5;
    int i;
    i = (int)f + (int)d;  // 符合：复杂表达式中每个浮点变量都使用强制转换
    printf("%d\n", i);
    return 0;
}