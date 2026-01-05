#include <stdio.h>

int process_first(int *a) {
    *a += 1;
    return *a;
}

int process_second(int *b) {
    *b *= 2;
    return *b;
}

int main(void) {
    int data1 = 5, data2 = 10;
    int result = process_first(&data1) + process_second(&data2);  // 符合：操作不同对象
    return result;
}