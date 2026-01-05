#include <stdio.h>

int main(void) {
    for (int i = 0, j = 10; i < 5; i++, j--) {  // 符合：使用多个局部变量作为循环控制
        printf("i=%d, j=%d\n", i, j);
    }
    return 0;
}