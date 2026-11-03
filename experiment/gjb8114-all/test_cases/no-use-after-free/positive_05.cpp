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
    int y = *alias;
    std::free(x);
    x = nullptr;
    alias = nullptr;

    return y;
}
