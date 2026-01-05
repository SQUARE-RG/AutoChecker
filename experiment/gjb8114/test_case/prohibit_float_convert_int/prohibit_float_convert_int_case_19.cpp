#include <stdio.h>

#define FLOAT_TO_INT(x) ((int)(x))

int main(void) {
    float f = 6.66f;
    int i = FLOAT_TO_INT(f);  // 符合：宏定义中封装了强制转换
    printf("%d\n", i);
    return 0;
}