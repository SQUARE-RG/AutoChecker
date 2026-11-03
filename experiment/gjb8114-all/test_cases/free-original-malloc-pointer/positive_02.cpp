#include <cstdlib>

int main() {
    int* base = static_cast<int*>(std::calloc(4, sizeof(int)));
    if (base == nullptr) {
        return 1;
    }
    int* cursor = base + 2;
    cursor[0] = 7;
    std::free(base);
    return 0;
}
