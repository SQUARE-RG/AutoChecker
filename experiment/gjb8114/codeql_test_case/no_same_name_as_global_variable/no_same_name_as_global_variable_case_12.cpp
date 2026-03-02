#include <stdio.h>

int total_count = 0;  // 全局变量

void add_to_count(int increment) {  // 符合：参数与全局变量不同名
    total_count += increment;
    printf("After adding %d: %d\n", increment, total_count);
}

int main(void) {
    add_to_count(5);
    add_to_count(3);
    return 0;
}