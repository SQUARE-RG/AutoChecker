#include <stdio.h>

int main(void) {
    int x = 5, y = 3, z = 1;
    if ((x & y) == z) {  // 符合：使用括号明确优先级
        printf("Condition met\n");
    }
    return 0;
}