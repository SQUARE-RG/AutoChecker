#include <iostream>

int main()
{
    unsigned int tbc = 0x80u;
    int i = ((tbc ^ 0x80u) == 0x80u) ? 1 : 2;
    return i;
}
