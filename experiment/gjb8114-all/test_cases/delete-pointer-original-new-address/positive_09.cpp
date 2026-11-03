#include <iostream>
#include <iterator>

int main() {
    int* p = new int[4];
    p[0] = 1;
    p[1] = 2;
    p[2] = 3;
    p[3] = 4;

    std::advance(p, 2);
    p[0] = 10;
    std::advance(p, -2);
    delete[] p;
    return 0;
}
