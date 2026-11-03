#include <iostream>

void process() {
    int* values = new int[10];
    for (int i = 0; i < 10; ++i) {
        values[i] = i;
    }
    std::cout << values[0];
    delete[] values;
}

int main() {
    process();
    return 0;
}
