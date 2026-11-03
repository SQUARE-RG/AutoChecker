#include <cstdlib>

int main()
{
    double* p = static_cast<double*>(std::malloc(sizeof(double)));
    if (p == nullptr)
    {
        return 1;
    }
    *p = 3.14;

    int i = 0;
    while (i < 1)
    {
        std::free(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
        ++i;
    }

    return 0;
}
