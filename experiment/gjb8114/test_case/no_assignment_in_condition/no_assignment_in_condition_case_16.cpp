#include <stdio.h>

int main(void) {
    int flag = 1;
    if (flag) {  // 符合：直接检查变量值，无赋值操作
        printf("Flag is set\n");
    }
    return 0;
}