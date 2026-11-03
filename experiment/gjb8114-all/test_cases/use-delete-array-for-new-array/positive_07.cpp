#include <iostream>

int main() {
    int *p = new int[5]();
    p[0] = 7;
    delete[] p;
    return 0;
}
