#include <cstddef>

static bool pointer_to_bool(int* p) {
    return static_cast<bool>(p);
}

int main() {
    int value = 0;
    int* ptr = &value;
    return pointer_to_bool(ptr) ? 0 : 1;
}
