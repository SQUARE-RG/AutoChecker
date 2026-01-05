#include <stdio.h>

int global_counter = 0;  // 全局变量

void test_proper_naming(void) {
    int local_counter = 5;  // 符合：局部变量与全局变量不同名
    printf("Local counter: %d\n", local_counter);
    printf("Global counter: %d\n", global_counter);
}

int main(void) {
    test_proper_naming();
    return 0;
}