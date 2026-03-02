#include <iostream>

void test_delete_array(void) {
    int *arr = new int[5];
    if (arr != nullptr) {
        for (int i = 0; i < 5; i++) {
            arr[i] = i * 10;
        }
        delete[] arr;  // 违反：数组delete后未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
}

int main(void) {
    test_delete_array();
    return 0;
}