#include <stdio.h>

int main(void) {
    FILE *fp;
    if (fp = fopen("test.txt", "r")) {  // 违反：在if条件中使用赋值语句
        // CHECK-MESSAGES: 禁止将赋值语句作为逻辑表达式 [gjb8114-r-1-6-3]
        fclose(fp);
    }
    return 0;
}