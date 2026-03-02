#include <stdio.h>

int counter = 0;

int increment_counter(void) {
    counter++;
    return counter;
}

int get_counter_value(void) {
    return counter;
}

int compute_result(void) {
    return increment_counter() * get_counter_value();  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
}