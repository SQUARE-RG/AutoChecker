#include <stdio.h>

int main(void) {
    for (int i = 0; i < 2; i++) {  // 符合：外层循环使用局部变量
        for (int j = 0; j < 3; j++) {  // 符合：内层循环使用局部变量
            printf("(%d,%d) ", i, j);
        }
        printf("\n");
    }
    return 0;
}