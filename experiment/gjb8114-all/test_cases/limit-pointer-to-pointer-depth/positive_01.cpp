#include <cstddef>

int main() {
    int value = 42;
    int *p1 = &value;
    int **p2 = &p1;

    int result = **p2;
    return result == 42 ? 0 : 1;
}
