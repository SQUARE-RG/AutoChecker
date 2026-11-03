#include <new>

int main() {
    int *p = new (std::nothrow) int(42);
    if (p != nullptr) {
        *p += 1;
        delete p;
    }
    return 0;
}
