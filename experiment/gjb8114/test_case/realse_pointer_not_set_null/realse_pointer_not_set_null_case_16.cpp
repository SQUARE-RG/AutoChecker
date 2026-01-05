#include <stdlib.h>

void test_multiple_proper_free(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 60;
        free(p);
        p = NULL;  // 第一次正确置空
        
        p = (int*)malloc(sizeof(int) * 2);
        if (p != NULL) {
            p[0] = 1;
            p[1] = 2;
            free(p);
            p = NULL;  // 符合：第二次释放后也正确置空
        }
    }
}

int main(void) {
    test_multiple_proper_free();
    return 0;
}