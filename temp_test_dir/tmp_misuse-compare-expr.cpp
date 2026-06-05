#include <stdio.h>

int main(void) {
    int a = 20, b = 10, result = 5;
    if (a - b != result) {  // 违反：减法和不等于运算符未使用括号
        //
        printf("Difference is not equal\n");
    }
    return 0;
}