#include <cstdlib>

int main() {
    int *p = static_cast<int*>(std::malloc(3 * sizeof(int)));
    if (p == nullptr) {
        return 1;
    }

    p[0] = 7;
    p[1] = 8;
    p[2] = 9;

    std::free(static_cast<void*>(p));
    return 0;
}
