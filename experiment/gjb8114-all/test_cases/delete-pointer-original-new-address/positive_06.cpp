#include <iostream>

int main() {
    int* p = new int[4];
    int* q = new int[4];
    for (int i = 0; i < 4; ++i) {
        p[i] = i;
        q[i] = i;
    }
    int* work = q;
    work += 2;
    delete[] p;
    delete[] q;
    return 0;
}
