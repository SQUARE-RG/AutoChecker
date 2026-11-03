#include <iostream>

struct Holder {
    int* base;
    int* work;
};

int main() {
    Holder h;
    h.base = new int[3];
    h.work = h.base;
    for (int i = 0; i < 3; ++i) {
        h.work[i] = i;
    }
    h.work += 1;
    delete[] h.base;
    h.base = nullptr;
    h.work = nullptr;
    return 0;
}
