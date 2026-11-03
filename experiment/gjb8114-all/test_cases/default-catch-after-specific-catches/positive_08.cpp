#include <iostream>
#include <stdexcept>
#include <exception>

int main()
{
    auto handler = []()
    {
        try
        {
            throw std::runtime_error("lambda error");
        }
        catch (const std::exception& e)
        {
            std::cout << e.what() << '\n';
        }
        catch (unsigned long code)
        {
            std::cout << code << '\n';
        }
        catch (...)
        {
            std::cout << "default" << '\n';
        }
    };

    handler();
    return 0;
}
