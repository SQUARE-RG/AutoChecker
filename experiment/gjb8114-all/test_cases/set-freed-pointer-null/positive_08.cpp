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
        std::free(p);
        p = nullptr;
    }

    return 0;
}
