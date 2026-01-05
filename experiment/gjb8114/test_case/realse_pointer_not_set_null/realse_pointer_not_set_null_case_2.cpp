#include <iostream>

void test_new_delete(void) {
    int *p = new int(20);
    if (p != nullptr) {
        delete p;  // 违反：释放后未置空
        // CHECK-MESSAGES: 禁止释放指针变量后未置空 [gjb8114-r-1-3-6]
    }
}

int main(void) {
    test_new_delete();
    return 0;
}