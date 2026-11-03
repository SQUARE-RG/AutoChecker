#include <cstddef>

void reset(int** pp) {
    if (pp != nullptr) {
        *pp = nullptr;
    }
}

int main() {
    int value = 7;
    int* p = &value;
    int** pp = &p;

    reset(pp);
    return 0;
}
