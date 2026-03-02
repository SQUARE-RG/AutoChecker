#include <stdio.h>

int check_value(int x) {
    if (x > 100) {
        return 1;
    } else if (x > 50) {
        return 2;
    } else {
        return 3;  // 符合：包含else分支
    }
}

int main(void) {
    printf("%d\n", check_value(75));
    return 0;
}