#include <iostream>

void releaseArray() {
    int* values = new int[4];
    for (int i = 0; i < 4; ++i) {
        values[i] = i + 1;
    }
    std::cout << values[0] << '\n';
    delete[] values;
    values = nullptr;
}

int main() {
    releaseArray();
    return 0;
}
