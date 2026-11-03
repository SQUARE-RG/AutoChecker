#include <iostream>
#include <cstddef>

int sum_values(const int* values, std::size_t count)
{
    int total = 0;
    for (std::size_t i = 0; i < count; ++i)
    {
        total += values[i];
    }
    return total;
}

int main()
{
    int data[5] = {1, 2, 3, 4, 5};
    const std::size_t count = sizeof(data) / sizeof(data[0]);
    std::cout << sum_values(data, count) << '\n';
    return 0;
}
