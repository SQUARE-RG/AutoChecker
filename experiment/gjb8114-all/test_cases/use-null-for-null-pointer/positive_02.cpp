#include <cstddef>

int main() {
    int value = 7;
    int* p = NULL;
    p = &value;
    return *p;
}
