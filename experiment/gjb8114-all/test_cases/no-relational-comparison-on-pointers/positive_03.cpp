#include <functional>

bool less_than(int* a, int* b)
{
    return std::less<int*>()(a, b);
}
