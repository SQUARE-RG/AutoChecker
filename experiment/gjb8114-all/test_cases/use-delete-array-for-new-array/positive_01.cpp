#include <iostream>

int main() {
    int* values = new int[3];
    values[0] = 1;
    values[1] = 2;
    values[2] = 3;
    delete[] values;
    values = nullptr;
    return 0;
}
