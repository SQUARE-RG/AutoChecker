#include <iostream>
#include <exception>
#include <stdexcept>

int main()
{
    try
    {
        throw std::runtime_error("boom");
    }
    catch (const std::exception &e)
    {
        std::cout << e.what() << std::endl;
    }
    catch (int value)
    {
        std::cout << value << std::endl;
    }
    catch (double value)
    {
        std::cout << value << std::endl;
    }
    catch (...)
    {
        std::cout << "default caught" << std::endl;
    }
    return 0;
}
