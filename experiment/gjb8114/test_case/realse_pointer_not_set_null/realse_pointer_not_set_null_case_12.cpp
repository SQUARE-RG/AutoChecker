#include <iostream>

void test_proper_new_delete(void) {
    int *p = new int(20);
    if (p != nullptr) {
        delete p;
        p = nullptr;  // 符合：C++中使用nullptr置空
    }
}

int main(void) {
    test_proper_new_delete();
    return 0;
}