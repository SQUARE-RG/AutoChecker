#include <stdio.h>

int global_value = 3;

int modify_global(int delta) {
    global_value += delta;
    return global_value;
}

int print_global(void) {
    return global_value;
}

void process_values(int a, int b) {
    // 处理值
}

int main(void) {
    process_values(modify_global(2), print_global());  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return 0;
}