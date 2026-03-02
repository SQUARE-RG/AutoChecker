#include <stdio.h>

int nested_check(int a, int b) {
    if (a > 0) {
        if (b > 0) {
            return 1;
        } else if (b < 0) {
            return 2;
        }
        return 3;  // 内层省略else，但这是单独的if-else if结构
    } else if (a < 0) {
        return 4;
    }
    return 5;  // 违反：外层if-else if省略else
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    printf("%d\n", nested_check(1, 1));
    return 0;
}