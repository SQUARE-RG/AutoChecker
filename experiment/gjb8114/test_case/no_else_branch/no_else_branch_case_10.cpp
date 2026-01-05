#include <stdio.h>

int complex_logic(int a, int b, int c) {
    if (a > b && b > c) {
        return 1;
    } else if (a < b && b < c) {
        return 2;
    } else if (a == b && b == c) {
        return 3;
    }
    return 4;  // 违反：复杂逻辑判断省略else
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    printf("%d\n", complex_logic(1, 2, 3));
    return 0;
}