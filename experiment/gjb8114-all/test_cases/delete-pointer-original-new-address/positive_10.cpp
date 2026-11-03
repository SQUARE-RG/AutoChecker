#include <iostream>

int main() {
    int* p = new int[4];
    p[0] = 1;
    p[1] = 2;
    p[2] = 3;
    p[3] = 4;

    int* q = reinterpret_cast<int*>(reinterpret_cast<char*>(p) + 2 * sizeof(int));
    q[0] = 5;
    delete[] p;
    return 0;
}
