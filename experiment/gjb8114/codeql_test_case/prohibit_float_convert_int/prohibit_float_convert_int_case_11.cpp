#include <stdio.h>

int main(void) {
    float f = 3.14f;
    int i;
    i = (int)f;  // 符合：使用显式强制转换
    printf("%d\n", i);
    return 0;
}