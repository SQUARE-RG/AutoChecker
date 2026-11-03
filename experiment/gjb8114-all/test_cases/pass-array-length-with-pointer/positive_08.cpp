#include <array>
#include <cstddef>

void zero(int* p, std::size_t n)
{
    for (std::size_t i = 0; i < n; ++i)
    {
        p[i] = 0;
    }
}

int main()
{
    std::array<int, 5> buf{1, 2, 3, 4, 5};
    zero(buf.data(), buf.size());
    return 0;
}
