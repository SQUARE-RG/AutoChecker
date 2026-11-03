#include <limits>

int main()
{
    unsigned int value = 1u;
    value <<= std::numeric_limits<unsigned int>::digits - 1;
    return 0;
}
