#include <cstddef>

void increment_all(int values[], std::size_t count)
{
    for (std::size_t i = 0; i < count; ++i) {
        values[i] = values[i] + 1;
    }
}

int main()
{
    int a[6] = {0, 1, 2, 3, 4, 5};
    increment_all(a, sizeof(a) / sizeof(a[0]));
    return 0;
}
