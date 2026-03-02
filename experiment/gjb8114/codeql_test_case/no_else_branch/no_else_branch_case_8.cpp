#include <stdio.h>
#include <stdbool.h>

bool validate_input(int input) {
    if (input < 0) {
        return false;
    } else if (input > 100) {
        return false;
    } else if (input % 2 == 0) {
        return true;
    }
    return false;  // 违反：布尔判断中省略else
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    printf("%d\n", validate_input(50));
    return 0;
}