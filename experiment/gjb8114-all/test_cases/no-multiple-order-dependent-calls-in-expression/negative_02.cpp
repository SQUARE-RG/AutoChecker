#include <cstdint>

int Next(int *pcData);
int Twice(int *pcData);
int Combine(int lhs, int rhs);

int main()
{
    int value = 3;
    int result = Combine(Next(&value), Twice(&value)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-14]
    return result;
}

int Next(int *pcData)
{
    int old = *pcData;
    *pcData = old + 1;
    return old;
}

int Twice(int *pcData)
{
    int old = *pcData;
    *pcData = old * 2;
    return old;
}

int Combine(int lhs, int rhs)
{
    return lhs * 10 + rhs;
}
