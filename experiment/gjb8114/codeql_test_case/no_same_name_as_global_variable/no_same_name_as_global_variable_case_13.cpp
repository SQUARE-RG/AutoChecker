#include <stdio.h>

int g_max_size = 100;  // 全局变量使用g_前缀

void calculate_size(void) {
    int local_size = 50;  // 符合：使用不同的命名约定
    if (local_size > g_max_size) {
        local_size = g_max_size;
    }
    printf("Calculated size: %d\n", local_size);
}

int main(void) {
    calculate_size();
    return 0;
}