#include <iostream>
#include <stdexcept>

void execute() try
{
    throw std::logic_error("bad logic");
}
catch (const std::logic_error& e)
{
    std::cout << e.what() << '\n';
}
catch (...)
{
    std::cout << "unknown" << '\n';
}

int main()
{
    execute();
    return 0;
}
