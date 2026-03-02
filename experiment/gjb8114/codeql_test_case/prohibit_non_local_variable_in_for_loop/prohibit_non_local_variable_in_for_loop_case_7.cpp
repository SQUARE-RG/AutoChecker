#include <stdio.h>

struct Config {
    int start;
    int end;
};

struct Config config = {0, 5};  // 全局结构体变量

int main(void) {
    for (config.start = 0; config.start < config.end; config.start++) {  // 违反：使用全局结构体成员作为循环控制变量
        // CHECK-MESSAGES: 禁止 for 循环控制变量使用非局部变量 [gjb8114-r-1-9-1]
        printf("%d ", config.start);
    }
    return 0;
}