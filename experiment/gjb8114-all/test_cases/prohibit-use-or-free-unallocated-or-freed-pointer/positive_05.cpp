#include <cstddef>

int main() {
    int* p = new int(7);
    if (p != nullptr) {
        *p = 8;
        delete p;
        p = nullptr;
    }
    return 0;
}
