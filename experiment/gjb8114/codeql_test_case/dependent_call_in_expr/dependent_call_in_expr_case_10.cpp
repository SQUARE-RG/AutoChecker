#include <stdio.h>

int data = 8;

int modify_data(int new_val) {
    data = new_val;
    return data;
}

int process_data(void) {
    return data * 2;
}

int main(void) {
    int result = process_data() + modify_data(15);  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}