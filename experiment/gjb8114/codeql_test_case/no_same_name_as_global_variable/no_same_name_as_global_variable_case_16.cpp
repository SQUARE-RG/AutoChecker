#include <stdio.h>

int the_global_var = 0;  // 全局变量

void foo(void) {
    int local_var = 0;  // 符合：局部变量与全局变量不同名
    local_var = 5;
    the_global_var = 10;
    printf("Local: %d, Global: %d\n", local_var, the_global_var);
}

int main(void) {
    foo();
    return 0;
}