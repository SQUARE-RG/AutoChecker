#include <cstddef>

int* staticLocalAddress()
{
    static int counter = 0;
    return &counter;
}
