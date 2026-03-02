#include <stdio.h>

struct BitFieldStruct {
    struct {
        unsigned int flag1 : 1;
        unsigned int flag2 : 3;
        unsigned int value : 8;
    };  // 违反：匿名结构体包含位域
    // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
};

int main(void) {
    struct BitFieldStruct bfs;
    bfs.flag1 = 1;
    return 0;
}