#include <cstddef>

void setAt(int* p, std::size_t n, std::size_t index, int value)
{
    if (index < n)
    {
        p[index] = value;
    }
}

int main()
{
    int data[6] = {1, 2, 3, 4, 5, 6};
    const std::size_t len = sizeof(data) / sizeof(data[0]);
    setAt(data, len, 0, 10);
    setAt(data, len, 5, 60);
    return data[0] + data[5];
}
