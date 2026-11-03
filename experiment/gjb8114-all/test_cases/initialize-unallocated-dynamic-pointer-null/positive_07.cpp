#include <cstdlib>

int main() {
    int* p = nullptr, *q = nullptr;
    p = static_cast<int*>(std::realloc(nullptr, sizeof(int)));
    if (p != nullptr) {
        *p = 42;
    }
    q = p;
    std::free(q);
    return 0;
}
