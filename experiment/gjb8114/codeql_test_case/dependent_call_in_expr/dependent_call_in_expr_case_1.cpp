#include <stdio.h>

int global_counter = 0;

int increment_global(void) {
    global_counter++;
    return global_counter;
}

int get_global(void) {
    return global_counter;
}

int main(void) {
    int result = increment_global() + get_global();  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}