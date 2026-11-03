#include <iostream>
#include <exception>

class BaseError : public std::exception
{
public:
    const char *what() const noexcept override
    {
        return "base error";
    }
};

class DerivedError : public BaseError
{
public:
    const char *what() const noexcept override
    {
        return "derived error";
    }
};

static void process()
{
    try
    {
        throw DerivedError();
    }
    catch (const DerivedError &e)
    {
        std::cout << e.what() << std::endl;
    }
    catch (const BaseError &e)
    {
        std::cout << e.what() << std::endl;
    }
    catch (...)
    {
        std::cout << "default caught" << std::endl;
    }
}

int main()
{
    process();
    return 0;
}
