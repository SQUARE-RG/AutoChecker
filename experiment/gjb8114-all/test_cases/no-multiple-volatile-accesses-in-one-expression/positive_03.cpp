#include <iostream>

int main()
{
    volatile int limit = 10;
    int value = 7;
    int localLimit = limit;
    if (value + localLimit > localLimit * 2)
    {
        std::cout << "above" << std::endl;
    }
    else
    {
        std::cout << "below" << std::endl;
    }
    return 0;
}
