#include <cstdint>

int main()
{
    unsigned int a = 0x5u;
    unsigned int b = 0x1u;
    unsigned int result = 0u;
    if ((a ^ b) != 0x4u)
    {
        result = 1u;
    }
    else
    {
        result = 2u;
    }
    return static_cast<int>(result);
}
