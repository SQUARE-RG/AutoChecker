#include <iostream>

int main()
{
    unsigned long count = 5UL;
    long limit = -1L;
    int loopCount = 0;

    while (limit <= count) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
    {
        ++loopCount;
        ++limit;
        if (loopCount > 10)
        {
            break;
        }
    }

    std::cout << loopCount << std::endl;
    return 0;
}
