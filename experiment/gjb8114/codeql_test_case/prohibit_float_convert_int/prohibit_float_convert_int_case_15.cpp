#include <stdio.h>

int main(void) {
    float f1 = 1.23f;
    float f2;
    f2 = f1;  // 符合：浮点变量间赋值不违反规则
    printf("%f\n", f2);
    return 0;
}