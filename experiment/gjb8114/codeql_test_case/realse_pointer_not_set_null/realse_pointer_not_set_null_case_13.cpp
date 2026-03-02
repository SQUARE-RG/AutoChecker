#include <stdlib.h>

void test_proper_array_free(void) {
    int *arr = (int*)malloc(sizeof(int) * 5);
    if (arr != NULL) {
        for (int i = 0; i < 5; i++) {
            arr[i] = i;
        }
        free(arr);
        arr = NULL;  // 符合：数组指针释放后置空
    }
}

int main(void) {
    test_proper_array_free();
    return 0;
}