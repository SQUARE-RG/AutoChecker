#include <stdio.h>

int main(void) {
    double d = 12.34;
    short s;
    s = (short)(int)d;  // 符合：使用多重强制转换明确意图
    printf("%d\n", s);
    return 0;
}