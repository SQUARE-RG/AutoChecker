#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return -1;
    }

    int* q = static_cast<int*>(std::realloc(p, sizeof(int) * 2));
    if (q == nullptr)
    {
        std::free(p);
        return -1;
    }

    *q = 42;
    std::free(q);
    return 0;
}
