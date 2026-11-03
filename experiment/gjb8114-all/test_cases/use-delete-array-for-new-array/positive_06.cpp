#include <iostream>

int main() {
    int (*p)[4] = new int[3][4];
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 4; ++j) {
            p[i][j] = i * 4 + j;
        }
    }
    delete[] p;
    return 0;
}
