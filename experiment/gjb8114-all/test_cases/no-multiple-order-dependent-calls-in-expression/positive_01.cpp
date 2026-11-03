#include <cstdint>

unsigned int Vel(unsigned int *pcData);
unsigned int Acc(unsigned int *pcData);

int main()
{
    unsigned int dis = 3;
    unsigned int temp1 = Vel(&dis);
    unsigned int temp2 = Acc(&dis);
    unsigned int hei = temp1 + temp2;
    return static_cast<int>(hei);
}

unsigned int Vel(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x * x;
    return x;
}

unsigned int Acc(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = 2 * x;
    return x;
}
