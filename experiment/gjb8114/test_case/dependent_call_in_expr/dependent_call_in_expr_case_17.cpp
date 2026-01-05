#include <stdio.h>
#include <string.h>

int main(void) {
    char str1[20] = "Hello";
    char str2[20] = "World";
    int result = strlen(str1) + strlen(str2);  // 符合：操作不同字符串
    return result;
}