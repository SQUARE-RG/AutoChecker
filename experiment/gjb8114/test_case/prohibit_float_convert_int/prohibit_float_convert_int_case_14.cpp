#include <stdio.h>

int main(void) {
    int a = 10;
    int b;
    b = a;  // 符合：整型变量间赋值不违反规则
    printf("%d\n", b);
    return 0;
}