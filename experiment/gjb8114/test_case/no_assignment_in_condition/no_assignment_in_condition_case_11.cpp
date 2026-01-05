#include <stdio.h>

int main(void) {
    int a = 5, b = 5;
    if (a == b) {  // 符合：使用比较运算符而非赋值
        printf("a equals b\n");
    }
    return 0;
}