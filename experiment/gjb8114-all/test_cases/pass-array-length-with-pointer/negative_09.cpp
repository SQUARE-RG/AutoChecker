#include <cstddef>

struct Accumulator
{
    int bias;
    explicit Accumulator(int b) : bias(b) {}

    void bump(int* p) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
    {
        for (int i = 0; i < 4; ++i)
        {
            p[i] += bias;
        }
    }
};

int main()
{
    int values[4] = {1, 2, 3, 4};
    Accumulator acc(3);
    acc.bump(values);
    return values[0];
}
