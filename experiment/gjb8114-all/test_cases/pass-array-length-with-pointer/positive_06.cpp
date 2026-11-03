#include <iostream>
#include <cstddef>

void scale_array(int values[8], std::size_t count)
{
    for (std::size_t i = 0; i < count; ++i)
    {
        values[i] *= 2;
    }
}

int main()
{
    int data[8] = {0, 1, 2, 3, 4, 5, 6, 7};
    const std::size_t count = sizeof(data) / sizeof(data[0]);
    scale_array(data, count);
    std::cout << data[7] << '\n';
    return 0;
}
