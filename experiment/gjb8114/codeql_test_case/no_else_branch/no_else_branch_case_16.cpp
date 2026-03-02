#include <stdio.h>

int process_input(int input) {
    if (input > 1000) {
        return input / 10;
    } else if (input > 100) {
        return input / 5;
    } else if (input > 10) {
        return input / 2;
    } else {
        // 处理边界情况
        if (input < 0) {
            return 0;
        } else {
            return input;
        }  // 符合：else分支包含完整逻辑
    }
}

int main(void) {
    printf("%d\n", process_input(5));
    return 0;
}