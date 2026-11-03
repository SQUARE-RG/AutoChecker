#include <cstdlib>

enum Flags
{
    A = 1 + 2,
    B,
    C
};

int main()
{
    Flags f = C;
    (void)f;
    return EXIT_SUCCESS;
}
