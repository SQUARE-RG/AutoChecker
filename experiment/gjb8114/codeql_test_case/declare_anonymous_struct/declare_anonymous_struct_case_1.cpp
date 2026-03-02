#include <stdio.h>

struct Outer {
    struct {
        int a;
        int b;
    };  // 违反：匿名结构体
    // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
};

int main(void) {
    struct Outer o;
    o.a = 1;
    o.b = 2;
    return 0;
}