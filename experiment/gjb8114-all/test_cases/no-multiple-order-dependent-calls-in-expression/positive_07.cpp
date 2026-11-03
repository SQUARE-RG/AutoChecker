#include <iostream>

unsigned int Bump(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x + 1;
    return x;
}

int main()
{
    unsigned int state = 0;
    std::cout << Bump(&state) << 0;
    return 0;
}
