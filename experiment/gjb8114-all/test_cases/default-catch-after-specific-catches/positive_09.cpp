#include <iostream>

int main()
{
    try
    {
        throw 42;
    }
    catch (...)
    {
        std::cout << "caught all" << std::endl;
    }
    return 0;
}
