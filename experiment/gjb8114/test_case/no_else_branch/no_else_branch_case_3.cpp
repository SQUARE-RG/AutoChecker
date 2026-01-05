#include <stdio.h>

void print_size(int size) {
    if (size > 1000) {
        printf("Large\n");
    } else if (size > 100) {
        printf("Medium\n");
    } else if (size > 10) {
        printf("Small\n");
    }
    printf("Tiny\n");  // 违反：void函数中省略else
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    print_size(5);
    return 0;
}