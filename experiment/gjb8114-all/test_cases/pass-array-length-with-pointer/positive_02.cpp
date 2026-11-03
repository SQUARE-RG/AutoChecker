#include <cstddef>

void clear_buffer(int* data, std::size_t count)
{
    for (std::size_t i = 0; i < count; ++i) {
        data[i] = 0;
    }
}

int main()
{
    int buffer[8] = {};
    clear_buffer(buffer, sizeof(buffer) / sizeof(buffer[0]));
    return 0;
}
