#include <cstdlib>

int main()
{
    int* base = static_cast<int*>(std::malloc(2 * sizeof(int)));
    if (base != nullptr)
    {
        base[0] = 10;
        base[1] = 20;
        std::free(base + 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-5]
    }
    return 0;
}
