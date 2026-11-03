#include <iostream>

int main() {
    int **p = new int*[5];
    p[0] = nullptr;
    p[1] = nullptr;
    delete[] p;
    p = nullptr;
    return 0;
}
