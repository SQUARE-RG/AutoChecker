#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char *buffer1 = (char *)malloc(100);
    char *buffer2 = (char *)malloc(100);
    
    strcpy(buffer1, "Test1");
    strcpy(buffer2, "Test2");
    
    int result = strlen(buffer1) + strlen(buffer2);  // 符合：操作不同内存区域
    
    free(buffer1);
    free(buffer2);
    return result;
}