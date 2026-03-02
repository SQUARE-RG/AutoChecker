#include <stdio.h>
#include <stdbool.h>

bool validate_range(int value) {
    if (value < 0) {
        return false;
    } else if (value > 1000) {
        return false;
    } else if (value % 5 == 0) {
        return true;
    } else {
        return false;  // 符合：布尔判断中包含else
    }
}

int main(void) {
    printf("%d\n", validate_range(25));
    return 0;
}