#include <cstdlib>

int main() {
    int* base = static_cast<int*>(std::malloc(3 * sizeof(int)));
    if (base == nullptr) {
        return 1;
    }
    int* p = base;
    p[0] = 1;
    p[1] = 2;
    ++p;
    std::free(base);
    return 0;
}
