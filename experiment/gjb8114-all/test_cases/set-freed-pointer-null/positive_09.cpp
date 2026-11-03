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
        std::free(p);
        p = nullptr;
        ++i;
    }

    return 0;
}
