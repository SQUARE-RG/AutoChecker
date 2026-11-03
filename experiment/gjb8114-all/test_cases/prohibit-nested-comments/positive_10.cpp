#include <iostream>

int classify(int mode)
{
    switch (mode)
    {
    case 0:
        /* note: a block comment may mention // as plain text */
        return 10;
    case 1:
        return 20;
    default:
        return -1;
    }
}

int main()
{
    std::cout << classify(0) << std::endl;
    return 0;
}
