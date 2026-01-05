#include <stdio.h>

struct PointerContainer {
    struct {
        int *ptr;
        char *name;
    };  // 违反：匿名结构体包含指针
    // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
};

int main(void) {
    struct PointerContainer pc;
    int value = 5;
    pc.ptr = &value;
    return 0;
}