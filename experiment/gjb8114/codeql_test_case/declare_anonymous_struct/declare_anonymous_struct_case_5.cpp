#include <stdio.h>

struct Mixed {
    int normal_member;
    struct {
        double x;
        double y;
    };  // 违反：混合匿名结构体
    // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
};

int main(void) {
    struct Mixed m;
    m.x = 3.14;
    return 0;
}