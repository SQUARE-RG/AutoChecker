#include <cstdint>

unsigned int Vel(unsigned int *pcData);
unsigned int Acc(unsigned int *pcData);

int main()
{
    unsigned int dis = 3;
    unsigned int hei = Vel(&dis) + Acc(&dis); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-14]
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
