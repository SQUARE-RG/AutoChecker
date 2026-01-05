#include <stdio.h>

int multi_condition_check(int x, int y, int z) {
    if (x > y && y > z) {
        return 1;
    } else if (x < y && y < z) {
        return 2;
    } else if (x == y && y == z) {
        return 3;
    } else {
        return 0;  // 符合：多变量条件包含else
    }
}

int main(void) {
    printf("%d\n", multi_condition_check(1, 2, 3));
    return 0;
}