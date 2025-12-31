#include <stdio.h>

int global_data = 100;  // 全局变量，但与局部变量不同名

int main(void) {
    for (int counter = 0; counter < 5; counter++) {  // 符合：局部变量与全局变量不同名
        printf("%d (global=%d)\n", counter, global_data);
    }
    return 0;
}