#include <cstdlib>

int main()
{
    int *x = static_cast<int *>(std::malloc(sizeof(int)));
    if (x == nullptr)
    {
        return 1;
    }

    *x = 1;
    int *alias = x;
    std::free(x);
    x = nullptr;

    int y = *alias; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    return y;
}
