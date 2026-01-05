#include <stdio.h>

int main(void) {
    int a = 5, b = 3;
    int sum;
    sum = a + b;  // 先赋值
    if (sum > 0) {  // 再比较
        printf("Sum is positive: %d\n", sum);
    }
    return 0;
}