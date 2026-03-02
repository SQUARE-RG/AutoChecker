#include <stdio.h>

int main(void) {
    int value = 2, threshold = 10;
    if ((value << 2) > threshold) {  // 符合：使用括号明确优先级
        printf("Value exceeds threshold\n");
    }
    return 0;
}