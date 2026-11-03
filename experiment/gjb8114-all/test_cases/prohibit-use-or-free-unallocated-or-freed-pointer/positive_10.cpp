#include <cstdlib>

int main()
{
    int* base = static_cast<int*>(std::malloc(sizeof(int)));
    if (base != nullptr)
    {
        int* alias = base;
        *alias = 7;
        int read_value = *base;
        alias = nullptr;
        std::free(base);
        base = nullptr;
        (void)read_value;
    }
    return 0;
}
