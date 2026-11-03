#include <cstdint>

int Next(int *pcData);
int Combine(int lhs, int rhs);

int main()
{
    int value = 5;
    int result = Combine(Next(&value), 100);
    return result;
}

int Next(int *pcData)
{
    int old = *pcData;
    *pcData = old + 1;
    return old;
}

int Combine(int lhs, int rhs)
{
    return lhs + rhs;
}
