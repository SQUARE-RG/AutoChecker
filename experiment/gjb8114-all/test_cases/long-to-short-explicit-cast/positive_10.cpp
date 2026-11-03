#include <cstddef>

short narrow(long lVar)
{
    return static_cast<short>(lVar);
}

int main()
{
    long lVar = 100000L;
    short sVar = narrow(lVar);
    return static_cast<int>(sVar);
}
