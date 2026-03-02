#include <stdio.h>

struct Container {
    union {
        int x;
        float y;
    };  // 违反：匿名联合体
    // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
};

int main(void) {
    struct Container c;
    c.x = 10;
    return 0;
}