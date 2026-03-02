#include <stdio.h>
#include <stdbool.h>

int main(void) {
    int x = 10, y = 5;
    bool is_greater = (x > y);  // 将比较结果存入布尔变量
    if (is_greater) {  // 符合：使用布尔变量进行判断
        printf("x is greater than y\n");
    }
    return 0;
}