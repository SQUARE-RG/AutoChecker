#include <stdio.h>

int main(void) {
    int isValid = 1;
    if (isValid == 1) {  // 符合：明确比较，避免赋值
        printf("Valid state\n");
    }
    return 0;
}