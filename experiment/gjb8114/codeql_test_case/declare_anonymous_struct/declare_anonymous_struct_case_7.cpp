#include <stdio.h>

struct GlobalStruct {
    struct {
        int global_data;
    };  // 违反：全局结构体中的匿名结构体
    // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
} global_instance;

int main(void) {
    global_instance.global_data = 42;
    return 0;
}