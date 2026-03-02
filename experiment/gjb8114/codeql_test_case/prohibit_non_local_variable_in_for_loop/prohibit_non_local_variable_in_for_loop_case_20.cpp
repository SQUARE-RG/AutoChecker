#include <stdio.h>

int main(void) {
    int values[] = {1, 2, 3, 4, 5};
    int length = 5;
    
    for (int index = 0; index < length; index++) {  // 符合：使用局部变量控制数组遍历
        printf("%d ", values[index]);
    }
    return 0;
}