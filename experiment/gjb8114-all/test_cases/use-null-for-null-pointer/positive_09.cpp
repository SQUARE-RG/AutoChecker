#include <cstddef>

int main() {
    int value = 1;
    int* pointers[2] = { &value, NULL };
    return pointers[0] == &value ? 0 : 1;
}
