#include <stdio.h>

int main(void) {
    int count = 5;
    while (count > 0) {  // 符合：使用比较运算符
        printf("%d ", count);
        count--;
    }
    return 0;
}