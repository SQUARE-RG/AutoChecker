#include <iostream>

unsigned int Bump(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x + 1;
    return x;
}

int main()
{
    unsigned int state = 0;
    std::cout << Bump(&state) << Bump(&state); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-14]
    return 0;
}
