#include <cstddef>
#include <iterator>

void scale(double* values, std::size_t n)
{
    for (std::size_t i = 0; i < n; ++i)
    {
        values[i] = values[i] * 2.0;
    }
}

int main()
{
    double samples[6] = {0.5, 1.5, 2.5, 3.5, 4.5, 5.5};
    scale(samples, std::size(samples));
    return 0;
}
