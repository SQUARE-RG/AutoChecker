#include <iostream>

int main()
{
    unsigned int limit = 5u;
    unsigned int index = 0u;
    while (index < limit)
    {
        ++index;
    }
    return static_cast<int>(index);
}
