#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return 1;
    }

    *p = 7;

    try
    {
        if (*p == 7)
        {
            throw 1;
        }
    }
    catch (int)
    {
        std::free(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
    }

    return 0;
}
