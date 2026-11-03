#include <iostream>

int main()
{
    int acc = 1;
    for (int i = 0; i < 5; ++i)
    {
        acc *= 2;
    }
    std::cout << acc << std::endl;
    return 0;
}
