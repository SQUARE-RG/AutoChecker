#include <stdio.h>

void foo(void) {
    for (int i = 0; i < 7; ++i) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", i);
    }
}

int main(void) {
    foo();
    return 0;
}