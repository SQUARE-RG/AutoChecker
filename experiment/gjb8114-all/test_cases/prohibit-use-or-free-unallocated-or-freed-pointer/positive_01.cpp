#include <cstdlib>
#include <iostream>

int main()
{
    int *p = static_cast<int *>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return 0;
    }
    *p = 10;
    int value = *p;
    std::free(p);
    p = nullptr;
    std::cout << value << '\n';
    return 0;
}
