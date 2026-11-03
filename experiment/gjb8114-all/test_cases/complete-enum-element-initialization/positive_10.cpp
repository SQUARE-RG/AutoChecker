#include <cstdlib>

enum Bits
{
    Bit0 = 1 << 0,
    Bit1 = 1 << 1,
    Bit2 = 1 << 2
};

int main()
{
    Bits b = Bit2;
    (void)b;
    return EXIT_SUCCESS;
}
