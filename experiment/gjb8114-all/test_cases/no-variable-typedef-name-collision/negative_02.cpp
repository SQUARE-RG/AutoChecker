#include <cstdint>
#include <iostream>

typedef uint32_t TCount;

int addOne(
    int TCount // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
)
{
    return TCount + 1;
}

int main()
{
    std::cout << addOne(4) << std::endl;
    return 0;
}
