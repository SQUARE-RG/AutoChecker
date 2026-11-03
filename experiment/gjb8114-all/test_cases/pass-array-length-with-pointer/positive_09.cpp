#include <cstddef>

struct Accumulator
{
    int bias;
    explicit Accumulator(int b) : bias(b) {}

    void bump(int* p, std::size_t n)
    {
        for (std::size_t i = 0; i < n; ++i)
        {
            p[i] += bias;
        }
    }
};

int main()
{
    int values[4] = {1, 2, 3, 4};
    Accumulator acc(3);
    acc.bump(values, sizeof(values) / sizeof(values[0]));
    return values[0];
}
