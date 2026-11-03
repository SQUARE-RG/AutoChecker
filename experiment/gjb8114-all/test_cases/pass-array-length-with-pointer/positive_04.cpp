#include <cstddef>

template <typename T>
void fillAll(T* p, std::size_t n)
{
    for (std::size_t i = 0; i < n; ++i) {
        p[i] = T{};
    }
}

int main() {
    int values[5] = {1, 2, 3, 4, 5};
    fillAll(values, sizeof(values) / sizeof(values[0]));
    return 0;
}
