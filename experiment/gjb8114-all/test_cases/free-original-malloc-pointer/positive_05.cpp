#include <cstdlib>

int main()
{
    int (*block)[4] = static_cast<int (*)[4]>(std::malloc(sizeof(int) * 8));
    if (block == nullptr)
    {
        return 1;
    }

    int (*original)[4] = block;
    (*block)[0] = 1;
    block = block + 1;
    (*block)[0] = 2;

    std::free(original);
    return 0;
}
