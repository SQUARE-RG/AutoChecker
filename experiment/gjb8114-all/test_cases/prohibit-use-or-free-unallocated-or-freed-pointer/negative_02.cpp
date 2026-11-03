#include <cstdlib>

int main()
{
    int *p = static_cast<int *>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return 0;
    }
    *p = 11;
    std::free(p);
    std::free(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-5]
    return 0;
}
