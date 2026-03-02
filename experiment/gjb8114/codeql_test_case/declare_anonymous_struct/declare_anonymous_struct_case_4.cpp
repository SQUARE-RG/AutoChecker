#include <stdio.h>

struct DataHolder {
    struct {
        int arr[5];
        char name[20];
    };  // 违反：匿名结构体包含数组
    // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
};

int main(void) {
    struct DataHolder dh;
    dh.arr[0] = 1;
    return 0;
}