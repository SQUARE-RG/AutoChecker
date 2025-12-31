#include <stdlib.h>

void test_conditional_not_null(void) {
    int *p = (int*)malloc(sizeof(int));
    if (p != NULL) {
        *p = 50;
        free(p);  // 违反：条件分支中释放后未置空
        //
    } else {
        p = NULL;
    }
}

int main(void) {
    test_conditional_not_null();
    return 0;
}