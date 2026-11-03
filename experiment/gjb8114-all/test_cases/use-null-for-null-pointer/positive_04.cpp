#include <cstddef>

static void take_ptr(int *ptr)
{
    if (ptr == NULL)
    {
        return;
    }
}

int main()
{
    take_ptr(NULL);
    return 0;
}
