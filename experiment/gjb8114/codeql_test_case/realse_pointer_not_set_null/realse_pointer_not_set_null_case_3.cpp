#include <stdlib.h>

void test_array_pointer(void) {
    int *arr = (int*)malloc(sizeof(int) * 5);
    if (arr != NULL) {
        for (int i = 0; i < 5; i++) {
            arr[i] = i;
        }
        free(arr);  // 违反：数组指针释放后未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
}

int main(void) {
    test_array_pointer();
    return 0;
}