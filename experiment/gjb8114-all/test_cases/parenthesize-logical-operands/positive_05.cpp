#include <iostream>

int main()
{
    unsigned int tbc = 0x80u;
    int i = 0;
    do
    {
        ++i;
    } while ((tbc & 0x80u) == 0x80u);
    return i;
}
