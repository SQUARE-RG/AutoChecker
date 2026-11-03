#include <cstddef>

int main() {
    int* values = new int[4]{1, 2, 3, 4};
    values[1] = 5;
    delete[] values;
    values = NULL;
    return 0;
}
