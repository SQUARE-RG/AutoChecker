#include <cstddef>

int main() {
    std::size_t n = 4;
    int* data = new int[n];
    for (std::size_t i = 0; i < n; ++i) {
        data[i] = static_cast<int>(i);
    }
    delete[] data;
    data = nullptr;
    return 0;
}
