#include <cstdlib>
#include <iostream>
#include <memory>

struct FreeDeleter
{
    void operator()(int *p) const
    {
        std::free(p);
    }
};

int main()
{
    std::unique_ptr<int, FreeDeleter> p(static_cast<int *>(std::malloc(sizeof(int))));
    if (!p)
    {
        return 0;
    }
    *p = 21;
    std::cout << *p << '\n';
    return 0;
}
