#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int main(void) {
    int x = 5, y = 3;
    int result = add(x, y) + multiply(x, y);  // 符合：函数间无数据依赖
    return result;
}