#include <iostream>

int main() {
    int *p = new int[3];
    int *pbak = p;
    p[0] = 1;
    p++;
    p[0] = 2;
    delete[] pbak;
    return 0;
}
