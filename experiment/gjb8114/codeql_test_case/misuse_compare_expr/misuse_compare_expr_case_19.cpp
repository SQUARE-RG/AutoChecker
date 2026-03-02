#include <stdio.h>

int main(void) {
    int a = 5, b = 3, c = 2, d = 4;
    if ((a & b) == (c | d)) {  // 符合：复杂表达式使用括号明确优先级
        printf("Complex condition met\n");
    }
    return 0;
}