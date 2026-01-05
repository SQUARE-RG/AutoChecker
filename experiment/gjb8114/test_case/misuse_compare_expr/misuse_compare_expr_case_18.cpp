#include <stdio.h>

int main(void) {
    int width = 5, height = 3, area_limit = 20;
    if ((width * height) >= area_limit) {  // 符合：使用括号明确优先级
        printf("Area meets or exceeds limit\n");
    }
    return 0;
}