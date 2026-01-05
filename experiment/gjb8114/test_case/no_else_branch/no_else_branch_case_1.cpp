#include <stdio.h>

int check_value(int x) {
    if (x > 100) {
        return 1;
    } else if (x > 50) {
        return 2;
    }
    return 3;  // 违反：省略了else分支
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    printf("%d\n", check_value(75));
    return 0;
}