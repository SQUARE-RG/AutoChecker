#include <stdio.h>

int main(void) {
    int num = 16, limit = 5;
    if ((num >> 1) < limit) {  // 符合：使用括号明确优先级
        printf("Within limit\n");
    }
    return 0;
}