#include <stdio.h>

int main(void) {
    int x = 3, y = 4, sum = 7;
    if ((x + y) == sum) {  // 符合：使用括号明确优先级
        printf("Sum is correct\n");
    }
    return 0;
}