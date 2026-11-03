#include <cstdlib>

int main() {
    void *raw = std::malloc(4 * sizeof(int));
    if (raw == nullptr) {
        return 1;
    }

    int *values = static_cast<int*>(raw);
    values[0] = 1;
    values[1] = 2;
    values[2] = 3;

    std::free(raw);
    return 0;
}
