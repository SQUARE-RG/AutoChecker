#include <climits>
#include <iostream>

int main()
{
    unsigned int u = 0;
    std::cin >> u;
    unsigned int result = 0;
    if (u < UINT_MAX)
    {
        result = 1;
    }
    else
    {
        result = 2;
    }
    return static_cast<int>(result);
}
