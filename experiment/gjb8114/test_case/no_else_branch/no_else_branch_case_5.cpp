#include <stdio.h>

int calculate_level(int value) {
    int level;
    if (value > 100) {
        level = 3;
    } else if (value > 50) {
        level = 2;
    } else if (value > 10) {
        level = 1;
    }
    level = 0;  // 违反：赋值语句代替else分支
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
    return level;
}

int main(void) {
    printf("%d\n", calculate_level(75));
    return 0;
}