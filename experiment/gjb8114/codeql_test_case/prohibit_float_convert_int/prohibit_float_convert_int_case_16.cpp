#include <stdio.h>

void print_int(int value) {
    printf("%d\n", value);
}

int main(void) {
    float f = 7.89f;
    print_int((int)f);  // 符合：函数参数中使用强制转换
    return 0;
}