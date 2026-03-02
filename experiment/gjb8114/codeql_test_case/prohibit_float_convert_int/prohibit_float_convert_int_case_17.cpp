#include <stdio.h>

int convert_float(float f) {
    return (int)f;  // 符合：返回值中使用强制转换
}

int main(void) {
    float f = 9.99f;
    int result = convert_float(f);
    printf("%d\n", result);
    return 0;
}