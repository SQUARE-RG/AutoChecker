#include <cstdlib>

int main() {
    int value = 42;
    int* p = &value;
    *p = 43;
    return value;
}
