#include <stdio.h>

int main(void) {
    int a = 20, b = 10, result = 5;
    if ((a - b) != result) {  // 符合：使用括号明确优先级
        printf("Difference is not equal\n");
    }
    return 0;
}