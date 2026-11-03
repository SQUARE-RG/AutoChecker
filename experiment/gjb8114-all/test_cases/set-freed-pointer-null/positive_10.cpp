#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return 1;
    }
    *p = 42;

    int** pp = &p;
    std::free(*pp);
    *pp = nullptr;

    return 0;
}
