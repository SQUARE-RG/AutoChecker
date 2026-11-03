#include <cstddef>

namespace
{
constexpr int kWidth = 6;
}

void scale(double* values) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    for (int i = 0; i < kWidth; ++i)
    {
        values[i] = values[i] * 2.0;
    }
}

int main()
{
    double samples[kWidth] = {0.5, 1.5, 2.5, 3.5, 4.5, 5.5};
    scale(samples);
    return 0;
}
