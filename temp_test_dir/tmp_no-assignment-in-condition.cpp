#include <stdio.h>

int main(void) {
    int a = 0, b = 0, c = 5;
    if (a == 0 || (b = c)) {  // 违反：在逻辑或表达式中使用赋值语句
        //
        printf("b is %d\n", b);
    }
    return 0;
}