#include <stdio.h>

int main(void) {
    int p = 10, q = 5, r = 15;
    if ((p ^ q) != r) {  // 符合：使用括号明确优先级
        printf("Condition met\n");
    }
    return 0;
}