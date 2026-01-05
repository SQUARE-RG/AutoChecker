#include <stdio.h>

int main(void) {
    int reg_var;  // 寄存器变量（局部）
    for (reg_var = 0; reg_var < 5; reg_var++) {  // 符合：寄存器变量也是局部变量
        printf("%d ", reg_var);
    }
    return 0;
}