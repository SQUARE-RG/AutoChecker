#include <stdio.h>

int nested_check(int a, int b) {
    if (a > 0) {
        if (b > 0) {
            return 1;
        } else {
            return 2;
        }
    } else if (a < 0) {
        return 3;
    } else {
        return 4;  // 符合：嵌套结构中正确使用else
    }
}

int main(void) {
    printf("%d\n", nested_check(1, 1));
    return 0;
}