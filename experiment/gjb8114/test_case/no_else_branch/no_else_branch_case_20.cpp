#include <stdio.h>

int complete_condition_chain(int value) {
    if (value >= 100) {
        return 4;
    } else if (value >= 75) {
        return 3;
    } else if (value >= 50) {
        return 2;
    } else if (value >= 25) {
        return 1;
    } else {
        return 0;  // 符合：完整条件链包含else
    }
}

int main(void) {
    printf("%d\n", complete_condition_chain(60));
    return 0;
}