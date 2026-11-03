#include <iostream>

int main() {
    int* p = new int[4];
    *(p + 1) = 7;
    delete[] p;
    return 0;
}
