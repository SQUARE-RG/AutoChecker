#include <stdio.h>

int global_data[5] = {1, 2, 3, 4, 5};  // 全局数组

void process_data(void) {
    int local_buffer[3] = {10, 20, 30};  // 符合：局部数组与全局数组不同名
    for (int i = 0; i < 3; i++) {
        printf("Local[%d] = %d, Global[%d] = %d\n", 
               i, local_buffer[i], i, global_data[i]);
    }
}

int main(void) {
    process_data();
    return 0;
}