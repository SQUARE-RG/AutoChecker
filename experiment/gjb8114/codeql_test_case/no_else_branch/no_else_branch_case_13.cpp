#include <stdio.h>

void handle_value(int value) {
    if (value > 100) {
        printf("High\n");
    } else if (value > 50) {
        printf("Medium\n");
    } else if (value > 10) {
        printf("Low\n");
    } else {
        /* 其他情况不处理 */  // 符合：空else分支带注释
    }
}

int main(void) {
    handle_value(5);
    return 0;
}