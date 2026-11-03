#include <iostream>
#include <memory>

int fun(void) {
    std::unique_ptr<int[]> owner(new int[3]);
    int *raw = owner.release();
    if (raw == nullptr) {
        return -1;
    }
    raw[0] = 1;
    raw[1] = 2;
    raw[2] = 3;
    delete[] raw;
    raw = nullptr;
    return 0;
}

int main(void) {
    return fun();
}
