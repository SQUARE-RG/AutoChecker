#include <stdio.h>

int main(void) {
    float f1 = 2.5f, f2 = 3.5f;
    int i;
    i = (int)(f1 + f2);  // 符合：浮点表达式结果使用强制转换
    printf("%d\n", i);
    return 0;
}