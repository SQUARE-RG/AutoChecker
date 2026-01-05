#include <stdio.h>

int counter(void) {
    static int count = 0;
    count++;
    return count;
}

int get_counter(void) {
    static int count = 0;
    return count;
}

int main(void) {
    int result = counter() * get_counter();  // 违反：相关函数调用
    // CHECK-MESSAGES: 禁止同一表达式中调用多个相关函数 [gjb8114-r-1-7-14]
    return result;
}