#include <iostream>

int main()
{
    unsigned int x = 2u;
    int y = -2;

    bool less = x > static_cast<unsigned int>(y);
    std::cout << less << std::endl;
    return 0;
}
