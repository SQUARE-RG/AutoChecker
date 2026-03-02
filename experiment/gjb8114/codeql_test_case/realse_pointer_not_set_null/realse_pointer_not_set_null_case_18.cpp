#include <stdlib.h>

void test_proper_before_return(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 90;
        free(p);
        p = NULL;  // 符合：函数退出前正确置空
    }
}

int main(void) {
    test_proper_before_return();
    return 0;
}