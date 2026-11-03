#include <cstdlib>

int main() {
    int *value = nullptr;
    value = static_cast<int *>(std::malloc(sizeof(int)));
    if (value != nullptr) {
        *value = 1;
        std::free(value);
    } else {
        return -1;
    }
    return 0;
}
