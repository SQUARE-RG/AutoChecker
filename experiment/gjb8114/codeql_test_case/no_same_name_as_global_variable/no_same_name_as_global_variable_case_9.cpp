#include <stdio.h>

int the_global_var = 0;  // 全局变量

void foo(void) {
    int the_global_var = 0;  // 违反：局部变量与全局变量同名
    // CHECK-MESSAGES: 禁止局部变量与全局变量同名 [gjb8114-r-1-13-1]
    the_global_var = 5;
    printf("Local: %d\n", the_global_var);
}

int main(void) {
    foo();
    printf("Global: %d\n", the_global_var);
    return 0;
}