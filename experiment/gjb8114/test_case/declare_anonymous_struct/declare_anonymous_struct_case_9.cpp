#include <stdio.h>

void test_function(void) {
    struct LocalStruct {
        struct {
            int local_data;
        };  // 违反：函数内的匿名结构体
        // CHECK-MESSAGES: 禁止结构体定义中含有匿名结构体 [gjb8114-r-1-1-9]
    } local_var;
    
    local_var.local_data = 10;
}

int main(void) {
    test_function();
    return 0;
}