#include <stdio.h>

int index_global = 0;  // 全局变量

void test_block_proper(void) {
    for (int i = 0; i < 3; i++) {  // 符合：循环变量与全局变量不同名
        int item_index = i;  // 符合：块内变量与全局变量不同名
        printf("Item %d at index %d\n", i, item_index);
    }
    printf("Global index: %d\n", index_global);
}

int main(void) {
    test_block_proper();
    return 0;
}