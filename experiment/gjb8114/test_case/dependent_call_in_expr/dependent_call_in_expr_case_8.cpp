#include <stdio.h>

int shared_data = 10;

int add_to_shared(int value) {
    shared_data += value;
    return shared_data;
}

int subtract_from_shared(int value) {
    shared_data -= value;
    return shared_data;
}

int main(void) {
    int value = 5;
    value += add_to_shared(3) + subtract_from_shared(2);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return value;
}