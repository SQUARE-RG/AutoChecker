#include <cstddef>

int main()
{
    short sVar = 10;
    long lVar = 100000L;
    sVar = static_cast<short>(sVar + lVar);
    return static_cast<int>(sVar);
}
