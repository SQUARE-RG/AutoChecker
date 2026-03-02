#include <stdio.h>

int main(void) {
    int x = 10, y = 5, z = 3, w = 12;
    if ((x + y) > (z - w)) {  // 符合：多重算术运算使用括号明确优先级
        printf("Comparison is valid\n");
    }
    return 0;
}