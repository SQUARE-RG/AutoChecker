#include <stdio.h>

int main(void) {
    int i, j = 3;
    for (i = 0; i = j; i++) {  // 违反：在for条件中使用赋值语句
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        printf("%d ", i);
    }
    return 0;
}