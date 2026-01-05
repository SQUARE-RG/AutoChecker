#include <iostream>

void test_proper_delete_array(void) {
    int *arr = new int[5];
    if (arr != nullptr) {
        for (int i = 0; i < 5; i++) {
            arr[i] = i * 10;
        }
        delete[] arr;
        arr = nullptr;  // 符合：数组delete后正确置空
    }
}

int main(void) {
    test_proper_delete_array();
    return 0;
}