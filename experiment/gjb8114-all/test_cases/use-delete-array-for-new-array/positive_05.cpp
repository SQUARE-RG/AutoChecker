#include <iostream>

int main() {
    using IntArray = int[10];
    IntArray* p = new IntArray[1];
    for (int i = 0; i < 10; ++i) {
        (*p)[i] = i;
    }
    delete[] p;
    return 0;
}
