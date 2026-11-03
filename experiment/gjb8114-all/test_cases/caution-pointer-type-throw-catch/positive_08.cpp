#include <exception>
#include <iostream>
#include <stdexcept>

int main()
{
    try
    {
        throw std::make_exception_ptr(std::runtime_error("boom"));
    }
    catch (std::exception_ptr ep)
    {
        try
        {
            std::rethrow_exception(ep);
        }
        catch (const std::exception &e)
        {
            std::cout << e.what() << std::endl;
        }
    }
    return 0;
}
