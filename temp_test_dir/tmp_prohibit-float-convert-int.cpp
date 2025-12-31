#include <stdio.h>

int main(void) {
    float f = 12.34f;
    int i = f;  // 违反：初始化时float变量直接赋给int变量未使用强制转换
    //
    printf("%d\n", i);
    return 0;
}