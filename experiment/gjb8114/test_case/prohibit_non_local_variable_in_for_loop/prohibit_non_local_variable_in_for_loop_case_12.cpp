#include <stdio.h>

void process_range(int start, int end) {
    for (int i = start; i < end; i++) {  // 符合：使用局部变量作为循环控制变量
        printf("%d ", i);
    }
}

int main(void) {
    process_range(0, 5);
    return 0;
}