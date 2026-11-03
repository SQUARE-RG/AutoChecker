#include <iostream>

int main()
{
    unsigned int x = 2u;
    int y = -2;
    int i;

    if (y < static_cast<int>(x))
    {
        i = 0;
    }
    else
    {
        i = 1;
    }

    std::cout << i << std::endl;
    return 0;
}
