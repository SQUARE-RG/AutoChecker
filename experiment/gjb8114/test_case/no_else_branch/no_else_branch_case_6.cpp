#include <stdio.h>

int foo(int x) {
    if (x > 1) {
        return 1;
    } else if (x < -1) {
        return -1;
    }
    return x;  // 违反：省略else分支
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    printf("%d\n", foo(0));
    return 0;
}