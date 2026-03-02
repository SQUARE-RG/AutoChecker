#include <stdio.h>

int check_temperature(int temp) {
    if (temp > 30) {
        return 1;  // 热
    } else if (temp > 20) {
        return 2;  // 温暖
    } else if (temp > 10) {
        return 3;  // 凉爽
    }
    return 4;  // 违反：多条件判断省略else
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    printf("%d\n", check_temperature(25));
    return 0;
}