#include <stdexcept>

double divide(double a, double b)
{
    if (b == 0.0)
    {
        throw std::domain_error("division by zero");
    }
    return a / b;
}

int main()
{
    try
    {
        (void)divide(1.0, 0.0);
        return 0;
    }
    catch (const std::domain_error&)
    {
        return 1;
    }
}
