#include <stdio.h>

int value = 10;

int increment_value(void) {
    value++;
    return value;
}

int get_value(void) {
    return value;
}

int main(void) {
    int first = increment_value();  // 先调用
    int second = get_value();       // 后调用
    int result = first + second;    // 符合：调用已分离
    return result;
}