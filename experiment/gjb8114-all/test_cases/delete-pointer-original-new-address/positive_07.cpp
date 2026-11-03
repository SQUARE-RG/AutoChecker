#include <iostream>

int fun(void) {
    int *p = new int[3];
    if (p == nullptr) {
        return -1;
    }
    p[0] = 1;
    p[1] = 2;
    p[2] = 3;
    delete[] p;
    p = nullptr;
    return 0;
}

int main(void) {
    return fun();
}
