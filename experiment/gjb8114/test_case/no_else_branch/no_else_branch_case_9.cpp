#include <stdio.h>
#include <ctype.h>

int classify_char(char c) {
    if (isdigit(c)) {
        return 1;
    } else if (isalpha(c)) {
        return 2;
    } else if (isspace(c)) {
        return 3;
    }
    return 4;  // 违反：字符分类中省略else
    // CHECK-MESSAGES: 禁止省略 if-else if 语句的 else 分支 [gjb8114-r-1-4-1]
}

int main(void) {
    printf("%d\n", classify_char('A'));
    return 0;
}