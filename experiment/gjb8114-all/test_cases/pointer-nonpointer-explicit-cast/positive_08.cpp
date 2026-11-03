#include <cstddef>

static bool accept_bool(bool flag) {
    return flag;
}

int main() {
    int value = 0;
    int* ptr = &value;
    return accept_bool(static_cast<bool>(ptr)) ? 0 : 1;
}
