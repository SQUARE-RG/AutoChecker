#include <stdio.h>

struct Complex {
    int id;
    struct {
        struct {
            int nested_value;
        };  // 违反：复杂匿名结构体嵌套
        // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
        char description[10];
    };
    double price;
};

int main(void) {
    struct Complex c;
    c.nested_value = 999;
    return 0;
}