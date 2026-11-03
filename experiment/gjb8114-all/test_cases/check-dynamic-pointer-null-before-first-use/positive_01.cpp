#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p != nullptr)
    {
        *p = 1;
    }
    else
    {
        return 1;
    }

    std::free(p);
    return 0;
}
