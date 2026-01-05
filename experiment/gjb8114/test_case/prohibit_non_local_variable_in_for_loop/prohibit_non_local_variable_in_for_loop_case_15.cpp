#include <stdio.h>

int main(void) {
    {  // 开始一个块作用域
        for (int j = 0; j < 3; j++) {  // 符合：在块作用域内使用局部变量
            printf("%d ", j);
        }
    }
    // j 在这里不可访问，符合局部变量规则
    return 0;
}