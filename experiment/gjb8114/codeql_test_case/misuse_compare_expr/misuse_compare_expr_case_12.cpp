#include <stdio.h>

int main(void) {
    int a = 6, b = 2, c = 2;
    if ((a | b) == c) {  // 符合：使用括号明确优先级
        printf("Condition met\n");
    }
    return 0;
}