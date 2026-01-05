#include <stdio.h>

int get_value(void) {
    return 42;
}

int main(void) {
    int value = get_value();  // 函数调用在条件外
    if (value > 0) {  // 符合：条件中只进行比较
        printf("Value is positive: %d\n", value);
    }
    return 0;
}