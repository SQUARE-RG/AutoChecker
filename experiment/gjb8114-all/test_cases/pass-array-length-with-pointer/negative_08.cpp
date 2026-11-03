#include <cstddef>

void zero(int* p) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    std::size_t n = sizeof(p) / sizeof(p[0]);
    for (std::size_t i = 0; i < n; ++i)
    {
        p[i] = 0;
    }
}

int main()
{
    int buf[5] = {1, 2, 3, 4, 5};
    zero(buf);
    return 0;
}
