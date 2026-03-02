#include <stdio.h>

int main(void) {
    for (int i = 0; i < 5; i++) {  // 符合：循环条件中使用比较运算符
        printf("%d ", i);
    }
    return 0;
}