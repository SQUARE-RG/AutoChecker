#include <stdio.h>

int index = 0;  // 全局变量

void test_block_shadowing(void) {
    for (int i = 0; i < 3; i++) {
        int index = i;  // 违反：代码块内局部变量与全局变量同名
        // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
        printf("Block index: %d\n", index);
    }
    printf("Global index: %d\n", index);
}

int main(void) {
    test_block_shadowing();
    return 0;
}