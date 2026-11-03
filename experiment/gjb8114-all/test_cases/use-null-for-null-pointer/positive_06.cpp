#include <cstddef>

void reset(int* ptr = NULL)
{
    if (ptr != NULL) {
        *ptr = 0;
    }
}

int main()
{
    int value = 7;
    reset(&value);
    return 0;
}
