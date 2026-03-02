#include <stdio.h>

struct Outer {
    struct {
        struct {
            int deep_value;
        };  // 违反：多层匿名结构体嵌套
        // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
    };
};

int main(void) {
    struct Outer o;
    o.deep_value = 100;
    return 0;
}