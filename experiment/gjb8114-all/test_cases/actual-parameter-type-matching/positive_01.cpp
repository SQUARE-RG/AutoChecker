#include <iostream>

unsigned int sum(unsigned int p1, unsigned short p2);

int main()
{
    unsigned int ix = 1;
    unsigned int iy = 2;
    unsigned int iz = sum(ix, static_cast<unsigned short>(iy));
    std::cout << iz << std::endl;
    return 0;
}

unsigned int sum(unsigned int p1, unsigned short p2)
{
    return p1 + static_cast<unsigned int>(p2);
}
