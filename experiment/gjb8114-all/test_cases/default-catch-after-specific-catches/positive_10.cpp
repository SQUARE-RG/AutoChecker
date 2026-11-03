#include <iostream>
#include <new>

void handle_allocation()
{
    try
    {
        throw std::bad_alloc();
    }
    catch (const std::bad_alloc& error)
    {
        std::cout << error.what() << std::endl;
    }
    catch (...)
    {
        std::cout << "unknown error" << std::endl;
    }
}

int main()
{
    handle_allocation();
    return 0;
}
