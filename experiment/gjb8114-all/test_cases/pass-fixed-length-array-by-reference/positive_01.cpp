#include <iostream>

void increment(int (&arr)[10]) {
    for (int i = 0; i < 10; ++i) {
        arr[i] += 1;
    }
}

int main() {
    int values[10] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    increment(values);
    return 0;
}
