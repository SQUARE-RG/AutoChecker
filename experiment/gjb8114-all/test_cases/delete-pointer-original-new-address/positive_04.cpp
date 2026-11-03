#include <iostream>

void writeSecond(int* ptr) {
    ++ptr;
    *ptr = 42;
}

int main() {
    int* p = new int[3];
    writeSecond(p);
    delete[] p;
    return 0;
}
