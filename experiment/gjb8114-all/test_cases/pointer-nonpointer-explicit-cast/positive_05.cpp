#include <cstdlib>

int main()
{
    unsigned int value = 1U;
    unsigned int* ptr = &value;
    bool flags[2] = { false, false };
    flags[0] = static_cast<bool>(ptr);
    return flags[0] ? 1 : 0;
}
