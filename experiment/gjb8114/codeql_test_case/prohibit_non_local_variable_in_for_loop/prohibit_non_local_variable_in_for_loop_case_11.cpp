#include <stdio.h>

int main(void) {
    for (int i = 0; i < 5; i++) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", i);
    }
    return 0;
}