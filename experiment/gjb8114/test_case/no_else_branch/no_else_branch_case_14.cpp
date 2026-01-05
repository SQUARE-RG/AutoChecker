#include <stdio.h>

int foo(int x) {
    if (x > 1) {
        return 1;
    } else if (x < -1) {
        return -1;
    } else {
        return x;  // 符合：包含else分支
    }
}

int main(void) {
    printf("%d\n", foo(0));
    return 0;
}