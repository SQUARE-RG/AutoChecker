#include <stdio.h>

int main(void) {
    int array[3] = {1, 2, 3};
    int index = 1;
    if (array[index] == 2) {  // 符合：直接访问和比较，无赋值操作
        printf("Found value 2 at index %d\n", index);
    }
    return 0;
}